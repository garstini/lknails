import json
from datetime import timedelta
from datetime import time
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking, BookingItem
from core.models import EmailTemplate, SiteSettings, WorkingHour
from services.models import Service, ServiceImage


class Command(BaseCommand):
    help = "Seed salon services and core settings"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[3]
        data = json.loads((base_dir / "data" / "services_seed.json").read_text(encoding="utf-8"))

        site_settings, _ = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "LK Nails & Lashes",
                "domain": "lknailslashes.de",
                "contact_email": "hello@lknailslashes.de",
                "contact_phone": "+49 000 000000",
                "address": "Germany",
                "instagram_url": "https://instagram.com/lknailslashes",
                "facebook_url": "https://facebook.com/lknailslashes",
                "currency_code": "EUR",
                "booking_slot_minutes": 15,
                "concurrent_capacity": 3,
                "timezone": "Europe/Berlin",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Site settings ready: {site_settings.site_name}"))

        for weekday in range(7):
            if weekday == 6:
                defaults = {"is_open": False, "open_time": time(0, 0), "close_time": time(0, 0)}
            elif weekday == 5:
                defaults = {"is_open": True, "open_time": time(10, 0), "close_time": time(19, 0)}
            else:
                defaults = {"is_open": True, "open_time": time(9, 0), "close_time": time(16, 0)}
            WorkingHour.objects.update_or_create(weekday=weekday, defaults=defaults)

        EmailTemplate.objects.get_or_create(
            template_type=EmailTemplate.TemplateType.ADMIN_BOOKING,
            defaults={
                "name": "Admin booking notification",
                "subject": "New booking {{ booking_reference }}",
                "body": (
                    "New booking {{ booking_reference }}\n\n"
                    "Customer: {{ customer_name }}\n"
                    "Phone: {{ phone }}\n"
                    "Email: {{ email }}\n"
                    "Appointment date: {{ appointment_date }}\n"
                    "Appointment time: {{ appointment_time }}\n"
                    "Total duration: {{ total_duration }} minutes\n"
                    "Total price: {{ total_price }}\n"
                    "Services:\n{{ service_lines }}\n\n"
                    "Note: {{ note }}"
                ),
                "html_body": (
                    "<h2>New booking {{ booking_reference }}</h2>"
                    "<p><strong>Customer:</strong> {{ customer_name }}</p>"
                    "<p><strong>Phone:</strong> {{ phone }}</p>"
                    "<p><strong>Email:</strong> {{ email }}</p>"
                    "<p><strong>Appointment date:</strong> {{ appointment_date }}</p>"
                    "<p><strong>Appointment time:</strong> {{ appointment_time }}</p>"
                    "<p><strong>Total duration:</strong> {{ total_duration }} minutes</p>"
                    "<p><strong>Total price:</strong> {{ total_price }}</p>"
                    "<p><strong>Services:</strong></p><pre>{{ service_lines }}</pre>"
                    "<p><strong>Note:</strong> {{ note }}</p>"
                ),
            },
        )
        EmailTemplate.objects.get_or_create(
            template_type=EmailTemplate.TemplateType.CUSTOMER_CONFIRMATION,
            defaults={
                "name": "Customer confirmation",
                "subject": "Booking confirmation {{ booking_reference }}",
                "body": (
                    "Hello {{ customer_name }},\n\n"
                    "Your booking {{ booking_reference }} has been received by {{ site_name }}.\n"
                    "Appointment date: {{ appointment_date }}\n"
                    "Appointment time: {{ appointment_time }}\n"
                    "Total duration: {{ total_duration }} minutes\n"
                    "Total price: {{ total_price }}\n"
                    "Services:\n{{ service_lines }}\n\n"
                    "Note: {{ note }}\n\n"
                    "Thank you,\n{{ site_name }}"
                ),
                "html_body": (
                    "<h2>Hello {{ customer_name }},</h2>"
                    "<p>Your booking <strong>{{ booking_reference }}</strong> has been received by {{ site_name }}.</p>"
                    "<p><strong>Appointment date:</strong> {{ appointment_date }}</p>"
                    "<p><strong>Appointment time:</strong> {{ appointment_time }}</p>"
                    "<p><strong>Total duration:</strong> {{ total_duration }} minutes</p>"
                    "<p><strong>Total price:</strong> {{ total_price }}</p>"
                    "<p><strong>Services:</strong></p><pre>{{ service_lines }}</pre>"
                    "<p><strong>Note:</strong> {{ note }}</p>"
                    "<p>Thank you,<br>{{ site_name }}</p>"
                ),
            },
        )

        for item in data:
            service, created = Service.objects.update_or_create(
                name=item["name"],
                category=item["category"],
                subcategory=item.get("subcategory", "-"),
                defaults={
                    "price": item["price"],
                    "duration_minutes": item["duration_minutes"],
                    "is_active": item.get("is_active", True),
                    "booking_count": item.get("bookings", 0),
                    "featured": item.get("bookings", 0) >= 15,
                },
            )
            if item.get("images"):
                ServiceImage.objects.get_or_create(service=service, alt_text=service.name, defaults={"is_primary": True})
            if created:
                self.stdout.write(f"Created service: {service.name}")

        first_service = Service.objects.filter(is_active=True).order_by("-booking_count", "name").first()
        if first_service and not Booking.objects.exists():
            starts_at = timezone.now() + timedelta(days=1)
            booking = Booking.objects.create(
                customer_name="Demo Guest",
                phone="+49 123 456789",
                email="guest@example.com",
                starts_at=starts_at,
                total_duration_minutes=first_service.duration_minutes,
                total_price=first_service.current_price,
            )
            BookingItem.objects.create(
                booking=booking,
                service=first_service,
                category=first_service.category,
                subcategory=first_service.subcategory,
                service_name=first_service.name,
                duration_minutes=first_service.duration_minutes,
                price=first_service.current_price,
            )
            booking.recalculate()
            booking.save()

        self.stdout.write(self.style.SUCCESS("Salon data seeded successfully."))
