from django.core import mail
from django.test import TestCase, override_settings

from core.email_utils import build_email_connection, send_configured_email
from core.models import EmailLog, SiteSettings


class EmailConfigTests(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_falls_back_to_default_backend_when_smtp_not_configured(self):
        SiteSettings.objects.create(site_name="LK")
        email_log = send_configured_email("Subject", "Body", ["guest@example.com"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(email_log.status, EmailLog.Status.SENT)

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

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_email_log_is_saved_with_recipients(self):
        SiteSettings.objects.create(site_name="LK")
        email_log = send_configured_email("Subject", "Body", ["guest@example.com"], template_type="smtp_test")
        self.assertEqual(email_log.recipient_list, "guest@example.com")
        self.assertEqual(email_log.template_type, "smtp_test")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_html_email_is_attached_when_provided(self):
        SiteSettings.objects.create(site_name="LK")
        send_configured_email("Subject", "Body", ["guest@example.com"], html_body="<p>Hello</p>")
        self.assertEqual(mail.outbox[0].alternatives[0].content, "<p>Hello</p>")
