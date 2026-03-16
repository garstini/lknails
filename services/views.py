from django.views.generic import ListView

from services.models import Service


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_active=True).prefetch_related("images", "promotions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grouped = {}
        for service in context["services"]:
            grouped.setdefault(service.category, {}).setdefault(service.subcategory, []).append(service)
        context["grouped_services"] = grouped
        return context


class GalleryView(ListView):
    model = Service
    template_name = "services/gallery.html"
    context_object_name = "services"

    def get_queryset(self):
        return (
            Service.objects.filter(is_active=True)
            .prefetch_related("images")
            .order_by("-featured", "-booking_count", "name")
        )
