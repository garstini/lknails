from django.core import mail
from django.test import TestCase, override_settings

from core.email_utils import build_email_connection, send_configured_email
from core.models import SiteSettings


class EmailConfigTests(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_falls_back_to_default_backend_when_smtp_not_configured(self):
        SiteSettings.objects.create(site_name="LK")
        send_configured_email("Subject", "Body", ["guest@example.com"])
        self.assertEqual(len(mail.outbox), 1)

    def test_builds_smtp_connection_when_google_smtp_fields_present(self):
        settings = SiteSettings.objects.create(
            site_name="LK",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_use_tls=True,
            smtp_username="owner@example.com",
            smtp_app_password="app-password",
        )
        connection = build_email_connection(settings)
        self.assertEqual(connection.host, "smtp.gmail.com")
        self.assertEqual(connection.port, 587)
        self.assertEqual(connection.username, "owner@example.com")
