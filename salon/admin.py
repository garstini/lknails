from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from .models import (
    ServiceCategory, Service, Staff, Customer, 
    Appointment, BlogPost, Gallery, Review, BusinessHours,
    EmailConfiguration, AppointmentService, SEOSettings, EmailLog, EmailTemplate, SalonSettings,
    DiscountCode, DiscountSettings
)
from .admin_dashboard import admin_dashboard, business_hours_config, email_config


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'name': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'duration_minutes', 'is_active', 'booking_count']
    list_filter = ['category', 'subcategory', 'is_active', 'created_at']
    search_fields = ['name', 'subcategory', 'description', 'meta_keywords']
    list_editable = ['price', 'is_active']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'subcategory', 'description', 'price', 'duration_minutes', 'image', 'is_active')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        })
    )
    
    def booking_count(self, obj):
        count = obj.appointmentservice_set.count()
        return f"{count} Buchungen"
    booking_count.short_description = "Buchungen"


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_available', 'created_at']
    list_filter = ['is_available', 'specialties']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    filter_horizontal = ['specialties']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']


class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1
    fields = ('service', 'price_at_booking', 'duration_at_booking')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Auto-populate price and duration from service
        return formset


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'staff', 'get_services', 'date', 'time', 'total_price', 'status', 'send_email_action']
    list_filter = ['status', 'date', 'staff', 'services__category']
    search_fields = ['customer__user__first_name', 'customer__user__last_name']
    list_editable = ['status']
    date_hierarchy = 'date'
    inlines = [AppointmentServiceInline]
    
    actions = ['confirm_appointments', 'send_confirmation_emails']
    
    def get_services(self, obj):
        return obj.get_services_list()
    get_services.short_description = "Services"
    
    def send_email_action(self, obj):
        if obj.status == 'confirmed':
            return format_html(
                '<a class="button" href="/admin/salon/appointment/{}/send_email/">E-Mail senden</a>',
                obj.pk
            )
        return "-"
    send_email_action.short_description = "E-Mail"
    send_email_action.allow_tags = True
    
    def confirm_appointments(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} Termine wurden bestätigt.')
    confirm_appointments.short_description = "Ausgewählte Termine bestätigen"
    
    def send_confirmation_emails(self, request, queryset):
        count = 0
        for appointment in queryset:
            if self.send_appointment_email(appointment):
                count += 1
        self.message_user(request, f'{count} E-Mails wurden versendet.')
    send_confirmation_emails.short_description = "Bestätigungs-E-Mails senden"
    
    def send_appointment_email(self, appointment):
        try:
            # Email logic will be implemented with email configuration
            return True
        except Exception as e:
            return False


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'content_format', 'is_published', 'created_at', 'view_count']
    list_filter = ['is_published', 'content_format', 'created_at', 'author']
    search_fields = ['title', 'content', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'content_format']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'content', 'content_format', 'featured_image', 'tags', 'is_published')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description'),
            'classes': ('collapse',)
        })
    )
    
    class Media:
        css = {
            'all': ('admin/css/blog_admin.css',)
        }
        js = ('admin/js/blog_admin.js',)
    
    actions = ['make_published', 'make_unpublished']
    
    def view_count(self, obj):
        # Placeholder - can implement view tracking later
        return "N/A"
    view_count.short_description = "Aufrufe"
    
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} Beiträge wurden veröffentlicht.')
    make_published.short_description = "Ausgewählte Beiträge veröffentlichen"
    
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} Beiträge wurden als Entwurf gespeichert.')
    make_unpublished.short_description = "Ausgewählte Beiträge als Entwurf"


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'is_featured', 'image_preview']
    list_filter = ['is_featured', 'service__category']
    search_fields = ['title', 'description']
    list_editable = ['is_featured']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'service', 'rating', 'star_display', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'service__category', 'created_at']
    search_fields = ['customer__user__first_name', 'customer__user__last_name', 'comment', 'service__name']
    list_editable = ['is_approved', 'is_featured']
    readonly_fields = ['customer', 'appointment', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Bewertungsdetails', {
            'fields': ('customer', 'appointment', 'service', 'staff', 'rating', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_reviews', 'reject_reviews', 'feature_reviews', 'unfeature_reviews']
    
    def customer_name(self, obj):
        return f"{obj.customer.user.first_name} {obj.customer.user.last_name}"
    customer_name.short_description = "Kunde"
    
    def star_display(self, obj):
        return obj.get_star_display()
    star_display.short_description = "Sterne"
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} Bewertungen wurden genehmigt.')
    approve_reviews.short_description = "Ausgewählte Bewertungen genehmigen"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} Bewertungen wurden abgelehnt.')
    reject_reviews.short_description = "Ausgewählte Bewertungen ablehnen"
    
    def feature_reviews(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} Bewertungen wurden als Featured markiert.')
    feature_reviews.short_description = "Als Featured markieren"
    
    def unfeature_reviews(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} Bewertungen sind nicht mehr Featured.')
    unfeature_reviews.short_description = "Featured Status entfernen"


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['day_display', 'is_open', 'opening_time', 'closing_time', 'break_display']
    list_editable = ['is_open', 'opening_time', 'closing_time']
    ordering = ['day_of_week']
    
    def day_display(self, obj):
        return dict(BusinessHours.DAYS_OF_WEEK)[obj.day_of_week]
    day_display.short_description = "Tag"
    
    def break_display(self, obj):
        if obj.break_start and obj.break_end:
            return f"{obj.break_start} - {obj.break_end}"
        return "Keine Pause"
    break_display.short_description = "Mittagspause"


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'from_email', 'smtp_server', 'smtp_port', 'is_active']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('name', 'from_email', 'admin_email', 'is_active')
        }),
        ('SMTP Configuration', {
            'fields': ('smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'use_tls'),
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make password field use password widget
        form.base_fields['smtp_password'].widget = forms.PasswordInput()
        return form
    
    def save_model(self, request, obj, form, change):
        if obj.is_active:
            # Deactivate all other configs
            EmailConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'service', 'price_at_booking', 'duration_at_booking']
    list_filter = ['service__category', 'appointment__date']
    search_fields = ['appointment__customer__user__first_name', 'service__name']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'email_type', 'status', 'sent_at', 'created_at']
    list_filter = ['email_type', 'status', 'sent_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('E-Mail Details', {
            'fields': ('recipient_email', 'recipient_name', 'sender_email', 'subject', 'email_type', 'status')
        }),
        ('Related Objects', {
            'fields': ('appointment', 'customer'),
            'classes': ('collapse',)
        }),
        ('Message Content', {
            'fields': ('message_preview', 'full_message'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('sent_at', 'error_message', 'created_at', 'updated_at'),
        })
    )
    
    actions = ['mark_as_sent', 'mark_as_failed']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='sent', sent_at=timezone.now())
        self.message_user(request, f'{updated} E-Mails wurden als gesendet markiert.')
    mark_as_sent.short_description = "Als gesendet markieren"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} E-Mails wurden als fehlgeschlagen markiert.')
    mark_as_failed.short_description = "Als fehlgeschlagen markieren"


@admin.register(SalonSettings)
class SalonSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time_slot_interval_minutes', 'opening_time', 'closing_time', 'max_concurrent_appointments']
    
    fieldsets = (
        ('Terminplanung', {
            'fields': ('time_slot_interval_minutes', 'buffer_time_minutes')
        }),
        ('Öffnungszeiten', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Personal & Kapazität', {
            'fields': ('max_concurrent_appointments',)
        }),
        ('Buchungseinstellungen', {
            'fields': ('min_advance_booking_hours', 'max_advance_booking_days')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SalonSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email_type', 'recipient_type', 'is_active', 'is_default', 'created_at', 'preview_action']
    list_filter = ['email_type', 'recipient_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'subject', 'html_content']
    list_editable = ['is_active']
    readonly_fields = ['available_variables', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'email_type', 'recipient_type', 'is_active', 'is_default')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Design Settings', {
            'fields': ('header_image', 'primary_color', 'background_color', 'footer_text'),
            'classes': ('collapse',)
        }),
        ('Available Variables', {
            'fields': ('available_variables',),
            'classes': ('collapse',),
            'description': 'Diese Variablen können in Ihrem Template verwendet werden:'
        }),
        ('Meta Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['make_default', 'activate_templates', 'deactivate_templates', 'preview_templates']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add widget for color fields
        form.base_fields['primary_color'].widget = forms.TextInput(attrs={
            'type': 'color', 
            'style': 'width: 50px; height: 30px;'
        })
        form.base_fields['background_color'].widget = forms.TextInput(attrs={
            'type': 'color', 
            'style': 'width: 50px; height: 30px;'
        })
        
        # Rich text editor for HTML content
        form.base_fields['html_content'].widget = forms.Textarea(attrs={
            'rows': 15,
            'style': 'font-family: monospace;'
        })
        
        return form
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def preview_action(self, obj):
        return format_html(
            '<a class="button" href="/admin/salon/emailtemplate/{}/preview/" target="_blank">Vorschau</a>',
            obj.pk
        )
    preview_action.short_description = "Vorschau"
    
    def make_default(self, request, queryset):
        for template in queryset:
            # Unset other defaults for same email type
            EmailTemplate.objects.filter(
                email_type=template.email_type,
                is_default=True
            ).exclude(id=template.id).update(is_default=False)
            
            # Set this as default
            template.is_default = True
            template.save()
        
        self.message_user(request, f'{queryset.count()} Templates wurden als Standard markiert.')
    make_default.short_description = "Als Standard-Template markieren"
    
    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} Templates wurden aktiviert.')
    activate_templates.short_description = "Templates aktivieren"
    
    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} Templates wurden deaktiviert.')
    deactivate_templates.short_description = "Templates deaktivieren"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:template_id>/preview/', self.admin_site.admin_view(self.preview_template), name='emailtemplate_preview'),
        ]
        return custom_urls + urls
    
    def preview_template(self, request, template_id):
        template = get_object_or_404(EmailTemplate, id=template_id)
        
        # Sample context for preview
        sample_context = {
            'customer_name': 'Max Mustermann',
            'customer_email': 'max@example.com',
            'customer_phone': '+49 30 123456789',
            'appointment_date': '15.12.2024',
            'appointment_time': '14:30',
            'appointment_services': 'Gel Maniküre, Wimpernverlängerung',
            'services_details': [
                {
                    'name': 'Gel Maniküre',
                    'price': '35.00',
                    'duration': '60',
                    'category': 'Nails',
                    'description': 'Professionelle Gel Maniküre mit UV-Lampe'
                },
                {
                    'name': 'Wimpernverlängerung',
                    'price': '54.00',
                    'duration': '60',
                    'category': 'Lashes',
                    'description': 'Klassische 1:1 Wimpernverlängerung'
                }
            ],
            'services_count': 2,
            'total_price': '89.00',
            'total_duration': '120 Minuten',
            'staff_name': 'Anna Schmidt',
            'appointment_notes': 'Kunde bevorzugt natürliche Farben',
            'notification_type': 'Neue Buchung',
            'admin_name': 'Admin',
            'salon_name': 'LK Nails & Lashes',
            'salon_phone': '+49 30 804997-18',
            'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany'
        }
        
        rendered = template.render_content(sample_context)
        
        return HttpResponse(rendered['html_content'], content_type='text/html')


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ['page_title', 'created_at']
    
    fieldsets = (
        ('Basic SEO', {
            'fields': ('page_title', 'meta_description', 'meta_keywords')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Structured Data', {
            'fields': ('structured_data',),
            'classes': ('collapse',)
        })
    )


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_percentage', 'email', 'status', 'valid_until', 'usage_count', 'max_usage']
    list_filter = ['discount_type', 'status', 'valid_from', 'valid_until']
    search_fields = ['code', 'email', 'customer__user__email', 'notes']
    list_editable = ['status']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin mã giảm giá', {
            'fields': ('code', 'discount_type', 'discount_percentage', 'max_discount_amount', 'min_order_amount')
        }),
        ('Người nhận', {
            'fields': ('customer', 'email')
        }),
        ('Cài đặt sử dụng', {
            'fields': ('max_usage', 'usage_count', 'status')
        }),
        ('Thời hạn', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Ghi chú', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['generate_first_time_codes', 'generate_birthday_codes', 'disable_codes', 'extend_validity']
    
    def generate_first_time_codes(self, request, queryset):
        """Generate first-time discount codes for selected customers"""
        count = 0
        for customer in Customer.objects.all():
            if not DiscountCode.objects.filter(customer=customer, discount_type='first_time').exists():
                # Generate first-time code logic here
                count += 1
        self.message_user(request, f'{count} mã giảm giá khách mới đã được tạo.')
    generate_first_time_codes.short_description = "Tạo mã giảm giá khách mới"
    
    def generate_birthday_codes(self, request, queryset):
        """Generate birthday discount codes"""
        from datetime import datetime, timedelta
        count = 0
        # Logic to generate birthday codes
        self.message_user(request, f'{count} mã giảm giá sinh nhật đã được tạo.')
    generate_birthday_codes.short_description = "Tạo mã giảm giá sinh nhật"
    
    def disable_codes(self, request, queryset):
        updated = queryset.update(status='disabled')
        self.message_user(request, f'{updated} mã giảm giá đã được vô hiệu hóa.')
    disable_codes.short_description = "Vô hiệu hóa mã đã chọn"
    
    def extend_validity(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        
        for code in queryset:
            code.valid_until = code.valid_until + timedelta(days=7)
            code.save()
        
        self.message_user(request, f'{queryset.count()} mã giảm giá đã được gia hạn 7 ngày.')
    extend_validity.short_description = "Gia hạn thêm 7 ngày"


@admin.register(DiscountSettings)
class DiscountSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'first_time_enabled', 'birthday_enabled', 'updated_at']
    
    fieldsets = (
        ('Mã giảm giá khách mới', {
            'fields': ('first_time_enabled', 'first_time_percentage', 'first_time_max_amount', 'first_time_min_order', 'first_time_validity_days')
        }),
        ('Mã giảm giá sinh nhật', {
            'fields': ('birthday_enabled', 'birthday_percentage', 'birthday_max_amount', 'birthday_min_order', 'birthday_validity_days', 'birthday_days_before')
        })
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not DiscountSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


# Custom Admin Site
class SalonAdminSite(admin.AdminSite):
    site_header = "LK Nails & Lashes Admin"
    site_title = "LK Nails & Lashes"
    index_title = "Salon Management"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', admin_dashboard, name='salon_dashboard'),
            path('business-hours/', business_hours_config, name='business_hours'),
            path('email-config/', email_config, name='email_config'),
        ]
        return custom_urls + urls


# Override default admin site
admin_site = SalonAdminSite(name='salon_admin')

# Re-register models with custom admin site
admin_site.register(ServiceCategory, ServiceCategoryAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Staff, StaffAdmin)
admin_site.register(Customer, CustomerAdmin)
admin_site.register(Appointment, AppointmentAdmin)
admin_site.register(BlogPost, BlogPostAdmin)
admin_site.register(Gallery, GalleryAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(BusinessHours, BusinessHoursAdmin)
admin_site.register(EmailConfiguration, EmailConfigurationAdmin)
admin_site.register(AppointmentService, AppointmentServiceAdmin)
admin_site.register(SEOSettings, SEOSettingsAdmin)
admin_site.register(EmailLog, EmailLogAdmin)
admin_site.register(EmailTemplate, EmailTemplateAdmin)
admin_site.register(SalonSettings, SalonSettingsAdmin)
admin_site.register(DiscountCode, DiscountCodeAdmin)
admin_site.register(DiscountSettings, DiscountSettingsAdmin)