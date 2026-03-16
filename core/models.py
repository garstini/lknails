from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="LK Nails & Lashes")
    domain = models.CharField(max_length=120, default="lknailslashes.de")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    address = models.CharField(max_length=255, blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    map_embed_url = models.URLField(blank=True)
    currency_code = models.CharField(max_length=3, default="EUR")
    smtp_host = models.CharField(max_length=120, blank=True, default="")
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_username = models.EmailField(blank=True)
    smtp_app_password = models.CharField(max_length=255, blank=True)
    smtp_sender_name = models.CharField(max_length=120, blank=True, default="")
    smtp_sender_email = models.EmailField(blank=True)
    booking_slot_minutes = models.PositiveIntegerField(default=15)
    concurrent_capacity = models.PositiveIntegerField(default=3)
    timezone = models.CharField(max_length=64, default="Europe/Berlin")

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def clean(self):
        if SiteSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError(_("Only one site settings record is allowed."))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name

    @property
    def smtp_is_configured(self):
        return bool(self.smtp_host and self.smtp_port and self.smtp_username and self.smtp_app_password)

    @property
    def default_from_email(self):
        sender_email = self.smtp_sender_email or self.smtp_username or self.contact_email
        if self.smtp_sender_name and sender_email:
            return f"{self.smtp_sender_name} <{sender_email}>"
        return sender_email or ""


class WorkingHour(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, _("Monday")
        TUESDAY = 1, _("Tuesday")
        WEDNESDAY = 2, _("Wednesday")
        THURSDAY = 3, _("Thursday")
        FRIDAY = 4, _("Friday")
        SATURDAY = 5, _("Saturday")
        SUNDAY = 6, _("Sunday")

    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices, unique=True)
    is_open = models.BooleanField(default=True)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        ordering = ["weekday"]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.open_time}-{self.close_time}"


class EmailTemplate(models.Model):
    class TemplateType(models.TextChoices):
        ADMIN_BOOKING = "admin_booking", _("Admin booking notification")
        CUSTOMER_CONFIRMATION = "customer_confirmation", _("Customer confirmation")

    name = models.CharField(max_length=120)
    template_type = models.CharField(max_length=32, choices=TemplateType.choices, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField(
        help_text=_(
            "Supported placeholders: customer_name, booking_reference, services, service_lines, total_price, "
            "total_duration, start_at, appointment_date, appointment_time, phone, email, note, site_name"
        )
    )

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    subject = models.CharField(max_length=200)
    recipient_list = models.TextField(help_text=_("Comma-separated recipient emails"))
    from_email = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    template_type = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_status_display()} - {self.subject}"
