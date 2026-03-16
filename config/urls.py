from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from bookings.views import BookingCreateView, BookingSuccessView, available_slots_view, calendar_view, dashboard_view
from core.views import HomeView
from core.seo_views import health_check, robots_txt, sitemap_xml
from services.views import GalleryView, ServiceListView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("health/", health_check, name="health_check"),
    path("api/available-slots/", available_slots_view, name="available_slots"),
    path("admin/dashboard/", dashboard_view),
    path("admin/calendar/", calendar_view),
]

urlpatterns += i18n_patterns(
    path("admin/dashboard/", dashboard_view, name="admin_dashboard"),
    path("admin/calendar/", calendar_view, name="admin_calendar"),
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("gallery/", GalleryView.as_view(), name="gallery"),
    path("booking/", BookingCreateView.as_view(), name="booking_create"),
    path("booking/success/", BookingSuccessView.as_view(), name="booking_success"),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
