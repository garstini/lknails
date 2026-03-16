from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from zoneinfo import ZoneInfo

from bookings.models import Booking
from bookings.views import get_available_start_slots, get_booking_timezone, is_booking_available
from core.models import SiteSettings, WorkingHour
from services.models import Service


class BookingAvailabilityTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(site_name="LK", concurrent_capacity=1, booking_slot_minutes=15)
        for weekday in range(7):
            if weekday == 6:
                WorkingHour.objects.create(weekday=weekday, is_open=False, open_time=time(0, 0), close_time=time(0, 0))
            elif weekday == 5:
                WorkingHour.objects.create(weekday=weekday, is_open=True, open_time=time(10, 0), close_time=time(19, 0))
            else:
                WorkingHour.objects.create(weekday=weekday, is_open=True, open_time=time(9, 0), close_time=time(16, 0))
        self.service = Service.objects.create(
            name="Test Service",
            category="Nails",
            subcategory="-",
            price=Decimal("25.00"),
            duration_minutes=60,
            is_active=True,
        )

    def test_overlapping_booking_is_rejected_when_capacity_reached(self):
        starts_at = timezone.now() + timedelta(days=1)
        Booking.objects.create(
            customer_name="Guest",
            phone="123",
            email="guest@example.com",
            starts_at=starts_at,
            total_duration_minutes=60,
            total_price=Decimal("25.00"),
        )
        self.assertFalse(is_booking_available(starts_at + timedelta(minutes=15), 30))

    def test_long_booking_checks_each_slot_instead_of_only_start_time(self):
        starts_at = timezone.now() + timedelta(days=1)
        Booking.objects.create(
            customer_name="First",
            phone="123",
            email="first@example.com",
            starts_at=starts_at + timedelta(minutes=30),
            total_duration_minutes=30,
            total_price=Decimal("25.00"),
        )
        self.assertFalse(is_booking_available(starts_at, 60))

    def test_available_slots_endpoint_returns_slots_for_selected_services(self):
        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.get(
            reverse("available_slots"),
            {"date": future_date, "services": [self.service.pk]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("slots", payload)
        self.assertEqual(payload["total_duration"], 60)
        self.assertFalse(payload["is_closed"])

    def test_available_slots_endpoint_marks_sunday_as_closed(self):
        today = timezone.localdate()
        days_until_sunday = (6 - today.weekday()) % 7
        sunday = today + timedelta(days=days_until_sunday or 7)
        response = self.client.get(
            reverse("available_slots"),
            {"date": sunday.isoformat(), "services": [self.service.pk]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["is_closed"])
        self.assertEqual(payload["slots"], [])

    def test_available_slots_endpoint_respects_weekday_working_hours(self):
        today = timezone.localdate()
        days_until_monday = (0 - today.weekday()) % 7
        monday = today + timedelta(days=days_until_monday or 7)
        response = self.client.get(
            reverse("available_slots"),
            {"date": monday.isoformat(), "services": [self.service.pk]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["working_hours"], {"open": "09:00", "close": "16:00"})
        labels = [slot["label"] for slot in payload["slots"]]
        self.assertIn("09:00", labels)
        self.assertNotIn("15:15", labels)

    def test_booking_rejects_past_date_in_germany_timezone(self):
        germany_today = timezone.now().astimezone(ZoneInfo("Europe/Berlin")).date()
        response = self.client.post(
            reverse("booking_create"),
            {
                "customer_name": "Past Guest",
                "phone": "123",
                "email": "past@example.com",
                "appointment_date": (germany_today - timedelta(days=1)).isoformat(),
                "appointment_time": "10:00",
                "services": [self.service.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "future date", status_code=200)

    def test_booking_rejects_closed_day(self):
        today = timezone.now().astimezone(ZoneInfo("Europe/Berlin")).date()
        days_until_sunday = (6 - today.weekday()) % 7
        sunday = today + timedelta(days=days_until_sunday or 7)
        response = self.client.post(
            reverse("booking_create"),
            {
                "customer_name": "Closed Guest",
                "phone": "123",
                "email": "closed@example.com",
                "appointment_date": sunday.isoformat(),
                "appointment_time": "10:00",
                "services": [self.service.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "closed on the selected day", status_code=200)

    def test_today_slots_do_not_include_past_times(self):
        germany_now = timezone.now().astimezone(get_booking_timezone())
        today = germany_now.date()
        weekday = today.weekday()
        if weekday == 6:
            return
        working_hour = WorkingHour.objects.get(weekday=weekday)
        working_hour.is_open = True
        working_hour.open_time = time(0, 0)
        working_hour.close_time = time(23, 45)
        working_hour.save()

        slots = get_available_start_slots(today, 60)
        if slots:
            self.assertGreaterEqual(slots[0], germany_now.replace(second=0, microsecond=0))

    def test_booking_success_page_shows_latest_booking_details(self):
        starts_at = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(
            customer_name="Guest",
            phone="123",
            email="guest@example.com",
            starts_at=starts_at,
            total_duration_minutes=60,
            total_price=Decimal("25.00"),
        )
        session = self.client.session
        session["latest_booking_id"] = booking.pk
        session.save()
        response = self.client.get(reverse("booking_success"))
        self.assertContains(response, booking.reference)

    def test_admin_dashboard_requires_staff_and_renders(self):
        user = get_user_model().objects.create_user("admin", password="pass", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_calendar_requires_staff_and_renders(self):
        user = get_user_model().objects.create_user("calendar", password="pass", is_staff=True)
        booking = Booking.objects.create(
            customer_name="Calendar Guest",
            phone="123",
            email="calendar@example.com",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=1),
            total_duration_minutes=60,
            total_price=Decimal("35.00"),
        )
        self.client.force_login(user)
        response = self.client.get(reverse("admin_calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("admin:bookings_booking_change", args=[booking.pk]))
        self.assertContains(response, reverse("admin:bookings_booking_delete", args=[booking.pk]))
