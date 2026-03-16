from django.views.generic import TemplateView

from bookings.models import Booking
from core.models import SiteSettings
from services.models import Service


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_services"] = Service.objects.filter(is_active=True, featured=True)[:6]
        context["top_services"] = Service.objects.filter(is_active=True).order_by("-booking_count", "name")[:6]
        context["latest_bookings"] = Booking.objects.exclude(status=Booking.Status.CANCELLED).order_by("-created_at")[:4]
        context["site_settings"] = SiteSettings.objects.first()
        return context
