from django.contrib import admin
from django import forms

from core.models import EmailLog, EmailTemplate, SiteSettings, WorkingHour


class SiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {
            "smtp_app_password": forms.PasswordInput(render_value=True),
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = (
        "site_name",
        "domain",
        "currency_code",
        "smtp_host",
        "smtp_username",
        "smtp_is_configured",
        "booking_slot_minutes",
        "concurrent_capacity",
        "timezone",
    )
    fieldsets = (
        ("General", {"fields": ("site_name", "domain", "currency_code", "timezone")}),
        ("Contact", {"fields": ("contact_email", "contact_phone", "address", "instagram_url", "facebook_url", "map_embed_url")}),
        (
            "SMTP Google / Email",
            {
                "fields": (
                    "smtp_host",
                    "smtp_port",
                    "smtp_use_tls",
                    "smtp_username",
                    "smtp_app_password",
                    "smtp_sender_name",
                    "smtp_sender_email",
                )
            },
        ),
        ("Booking", {"fields": ("booking_slot_minutes", "concurrent_capacity")}),
    )


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ("weekday", "is_open", "open_time", "close_time")
    list_editable = ("is_open", "open_time", "close_time")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "subject")
    fields = ("name", "template_type", "subject", "body", "html_body")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "status", "subject", "recipient_list", "template_type")
    list_filter = ("status", "template_type", "created_at")
    search_fields = ("subject", "recipient_list", "error_message")
    readonly_fields = ("created_at",)
