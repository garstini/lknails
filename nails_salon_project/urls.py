"""nails_salon_project URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from salon.admin_dashboard import admin_dashboard, business_hours_config, email_config, test_email, activate_email_config

# URL patterns that don't need language prefix
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# URL patterns with language prefix
urlpatterns += i18n_patterns(
    path('salon-admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('salon-admin/business-hours/', business_hours_config, name='business_hours_config'),
    path('salon-admin/email-config/', email_config, name='email_config'),
    path('salon-admin/test-email/<int:config_id>/', test_email, name='test_email'),
    path('salon-admin/activate-email-config/<int:config_id>/', activate_email_config, name='activate_email_config'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('salon.urls')),
)

# Always serve media files in development and production for this demo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)