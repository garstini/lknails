from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from bookings.views import is_booking_available
from core.models import SiteSettings, WorkingHour
from services.models import Service


class BookingAvailabilityTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(site_name="LK", concurrent_capacity=1, booking_slot_minutes=15)
        for weekday in range(7):
            WorkingHour.objects.create(weekday=weekday, is_open=True, open_time=time(9, 0), close_time=time(18, 0))
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
        self.client.force_login(user)
        response = self.client.get(reverse("admin_calendar"))
        self.assertEqual(response.status_code, 200)
