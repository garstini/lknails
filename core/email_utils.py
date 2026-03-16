from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from core.models import SiteSettings


def build_email_connection(site_settings=None):
    site_settings = site_settings or SiteSettings.objects.first()
    if site_settings and site_settings.smtp_is_configured:
        return get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=site_settings.smtp_host,
            port=site_settings.smtp_port,
            username=site_settings.smtp_username,
            password=site_settings.smtp_app_password,
            use_tls=site_settings.smtp_use_tls,
            fail_silently=True,
        )
    return get_connection(backend=settings.EMAIL_BACKEND, fail_silently=True)


def send_configured_email(subject, body, recipient_list, site_settings=None):
    site_settings = site_settings or SiteSettings.objects.first()
    connection = build_email_connection(site_settings)
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=(site_settings.default_from_email if site_settings else settings.DEFAULT_FROM_EMAIL),
        to=recipient_list,
        connection=connection,
    )
    return message.send(fail_silently=True)
