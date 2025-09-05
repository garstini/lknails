from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    subcategory = models.CharField(max_length=100, blank=True, help_text="Subcategory like 'Volume 4D-5D', 'Classic 1:1'")
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Titel (falls leer, wird Name verwendet)")
    meta_description = models.TextField(max_length=160, blank=True, help_text="Meta Description für Suchmaschinen")
    meta_keywords = models.TextField(blank=True, help_text="SEO Keywords (komma-getrennt)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.subcategory:
            return f"{self.subcategory} • {self.name} - €{self.price}"
        return f"{self.name} - €{self.price}"

    def get_duration_display(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        return f"{minutes}min"

    def get_average_rating(self):
        reviews = self.review_set.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    def get_review_count(self):
        return self.review_set.filter(is_approved=True).count()

    def get_star_display(self):
        avg_rating = self.get_average_rating()
        if avg_rating:
            full_stars = int(avg_rating)
            half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            return '★' * full_stars + ('☆' if half_star else '') + '☆' * empty_stars
        return '☆☆☆☆☆'


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    specialties = models.ManyToManyField(ServiceCategory, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Staff"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_available_slots(self, date):
        start_time = time(9, 0)
        end_time = time(18, 0)
        slot_duration = 15
        
        slots = []
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        while current_time < end_datetime:
            is_available = not self.appointments.filter(
                date=date,
                time=current_time.time(),
                status__in=['confirmed', 'completed']
            ).exists()
            
            slots.append({
                'time': current_time.time(),
                'available': is_available
            })
            current_time += timedelta(minutes=slot_duration)
        
        return slots


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Special requests or notes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, through='AppointmentService', help_text="Gebuchte Services")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_duration = models.PositiveIntegerField(default=0, help_text="Gesamtdauer in Minuten")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'date', 'time'],
                condition=models.Q(status__in=['pending', 'confirmed', 'completed']),
                name='unique_active_appointment_per_staff_datetime'
            )
        ]

    def __str__(self):
        services_count = self.services.count()
        return f"{self.customer} - {services_count} Service(s) - {self.date} {self.time}"

    @property
    def end_time(self):
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(minutes=self.total_duration)
        return end_datetime.time()
    
    def get_services_list(self):
        return ", ".join([service.name for service in self.services.all()])
    
    def calculate_totals(self):
        """Berechne Gesamtpreis und -dauer basierend auf gebuchten Services"""
        appointment_services = self.appointment_services.all()
        self.total_price = sum(aps.price_at_booking for aps in appointment_services)
        self.total_duration = sum(aps.duration_at_booking for aps in appointment_services)
        self.save()


class BlogPost(models.Model):
    CONTENT_FORMAT_CHOICES = [
        ('html', 'HTML'),
        ('text', 'Plain Text'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    content_format = models.CharField(max_length=10, choices=CONTENT_FORMAT_CHOICES, default='html', help_text="Content format type")
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Titel (falls leer, wird Titel verwendet)")
    meta_description = models.TextField(max_length=160, blank=True, help_text="Meta Description für Suchmaschinen")
    meta_keywords = models.TextField(blank=True, help_text="SEO Keywords (komma-getrennt)")
    og_title = models.CharField(max_length=100, blank=True, help_text="Open Graph Titel")
    og_description = models.TextField(max_length=200, blank=True, help_text="Open Graph Description")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})


class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Gallery"

    def __str__(self):
        return self.title


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Stern - Sehr schlecht'),
        (2, '2 Sterne - Schlecht'),
        (3, '3 Sterne - Durchschnittlich'),
        (4, '4 Sterne - Gut'),
        (5, '5 Sterne - Ausgezeichnet'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE, blank=True, null=True, related_name='review')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(help_text="Teilen Sie Ihre Erfahrung mit anderen Kunden")
    is_approved = models.BooleanField(default=True, help_text="Bewertung öffentlich sichtbar")
    is_featured = models.BooleanField(default=False, help_text="Als Featured Review anzeigen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bewertung"
        verbose_name_plural = "Bewertungen"

    def __str__(self):
        return f"{self.customer} - {self.rating} Sterne ({self.service or 'Allgemein'})"

    def get_star_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def get_rating_percentage(self):
        return (self.rating / 5) * 100


class BusinessHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Montag'),
        (1, 'Dienstag'),
        (2, 'Mittwoch'),
        (3, 'Donnerstag'),
        (4, 'Freitag'),
        (5, 'Samstag'),
        (6, 'Sonntag'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(default=time(9, 0))
    closing_time = models.TimeField(default=time(18, 0))
    break_start = models.TimeField(blank=True, null=True, help_text="Mittagspause Start")
    break_end = models.TimeField(blank=True, null=True, help_text="Mittagspause Ende")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Öffnungszeit"
        verbose_name_plural = "Öffnungszeiten"
        ordering = ['day_of_week']

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        if self.is_open:
            return f"{day_name}: {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return f"{day_name}: Geschlossen"


class EmailConfiguration(models.Model):
    name = models.CharField(max_length=100, default="Standard Konfiguration")
    smtp_server = models.CharField(max_length=255, default="smtp.gmail.com")
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.EmailField()
    smtp_password = models.CharField(max_length=255, help_text="App-Passwort für Gmail")
    use_tls = models.BooleanField(default=True)
    from_email = models.EmailField()
    admin_email = models.EmailField(help_text="E-Mail für Admin-Benachrichtigungen")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "E-Mail Konfiguration"
        verbose_name_plural = "E-Mail Konfigurationen"

    def __str__(self):
        return f"{self.name} - {self.from_email}"


class AppointmentService(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, related_name='appointment_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price_at_booking = models.DecimalField(max_digits=8, decimal_places=2, help_text="Preis zum Zeitpunkt der Buchung")
    duration_at_booking = models.PositiveIntegerField(help_text="Dauer in Minuten zum Zeitpunkt der Buchung")
    
    class Meta:
        unique_together = ['appointment', 'service']
        verbose_name = "Termin Service"
        verbose_name_plural = "Termin Services"

    def __str__(self):
        return f"{self.appointment.customer} - {self.service.name}"


class SEOSettings(models.Model):
    page_title = models.CharField(max_length=200, help_text="SEO Titel für die Seite")
    meta_description = models.TextField(max_length=160, help_text="Meta Description für Suchmaschinen")
    meta_keywords = models.TextField(blank=True, help_text="Meta Keywords (komma-getrennt)")
    og_title = models.CharField(max_length=100, blank=True, help_text="Open Graph Titel")
    og_description = models.TextField(max_length=200, blank=True, help_text="Open Graph Description")
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True, help_text="Open Graph Bild")
    
    # JSON-LD structured data
    structured_data = models.JSONField(blank=True, null=True, help_text="JSON-LD Structured Data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO Einstellung"
        verbose_name_plural = "SEO Einstellungen"

    def __str__(self):
        return self.page_title


class EmailLog(models.Model):
    EMAIL_TYPES = [
        ('appointment_confirmation', 'Terminbestätigung'),
        ('appointment_cancellation', 'Terminabsage'),
        ('appointment_reminder', 'Terminerinnerung'),
        ('newsletter', 'Newsletter'),
        ('promotional', 'Werbung'),
        ('admin_notification', 'Admin Benachrichtigung'),
        ('other', 'Sonstiges'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Gesendet'),
        ('failed', 'Fehlgeschlagen'),
        ('pending', 'Ausstehend'),
    ]
    
    recipient_email = models.EmailField(help_text="E-Mail-Adresse des Empfängers")
    recipient_name = models.CharField(max_length=200, blank=True, help_text="Name des Empfängers")
    sender_email = models.EmailField(help_text="E-Mail-Adresse des Absenders")
    subject = models.CharField(max_length=255, help_text="E-Mail Betreff")
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES, help_text="Art der E-Mail")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Status der E-Mail")
    
    # Related objects
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, blank=True, null=True, help_text="Zugehöriger Termin")
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True, help_text="Zugehöriger Kunde")
    
    # Email content
    message_preview = models.TextField(max_length=500, blank=True, help_text="Vorschau der Nachricht (erste 500 Zeichen)")
    full_message = models.TextField(blank=True, help_text="Vollständige Nachricht")
    
    # Tracking
    sent_at = models.DateTimeField(blank=True, null=True, help_text="Zeitpunkt des Versands")
    error_message = models.TextField(blank=True, help_text="Fehlermeldung falls Versand fehlgeschlagen")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "E-Mail Log"
        verbose_name_plural = "E-Mail Logs"

    def __str__(self):
        return f"{self.get_email_type_display()} an {self.recipient_email} - {self.get_status_display()}"
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        return {
            'sent': 'badge-success',
            'failed': 'badge-danger',
            'pending': 'badge-warning',
        }.get(self.status, 'badge-secondary')


class EmailTemplate(models.Model):
    EMAIL_TYPES = [
        ('appointment_confirmation', 'Terminbestätigung'),
        ('appointment_cancellation', 'Terminabsage'),
        ('appointment_reminder', 'Terminerinnerung'),
        ('welcome_email', 'Willkommens-E-Mail'),
        ('promotional', 'Werbung'),
        ('newsletter', 'Newsletter'),
        ('birthday_greeting', 'Geburtstagswünsche'),
        ('follow_up', 'Nachfass-E-Mail'),
        ('admin_notification', 'Admin Benachrichtigung'),
        ('custom', 'Benutzerdefiniert'),
    ]
    
    RECIPIENT_TYPES = [
        ('customer', 'An Kunden senden'),
        ('admin', 'An Admin senden'),
        ('both', 'An Kunden und Admin senden'),
    ]
    
    name = models.CharField(max_length=200, help_text="Name des Templates")
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES, help_text="Art der E-Mail")
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPES, default='customer', help_text="An wen soll die E-Mail gesendet werden")
    subject = models.CharField(max_length=255, help_text="E-Mail Betreff (kann Variablen enthalten)")
    html_content = models.TextField(help_text="HTML E-Mail Inhalt")
    text_content = models.TextField(blank=True, help_text="Text E-Mail Inhalt (optional)")
    
    # Template settings
    is_active = models.BooleanField(default=True, help_text="Template aktiv")
    is_default = models.BooleanField(default=False, help_text="Standard-Template für diesen E-Mail-Typ")
    
    # Available variables documentation
    available_variables = models.TextField(
        blank=True,
        help_text="Verfügbare Variablen für dieses Template (automatisch generiert)"
    )
    
    # Design settings
    header_image = models.ImageField(upload_to='email_templates/', blank=True, null=True, help_text="Header-Bild für E-Mail")
    footer_text = models.TextField(blank=True, help_text="Footer-Text")
    primary_color = models.CharField(max_length=7, default="#e91e63", help_text="Primärfarbe (Hex)")
    background_color = models.CharField(max_length=7, default="#ffffff", help_text="Hintergrundfarbe (Hex)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates')

    class Meta:
        ordering = ['email_type', 'name']
        verbose_name = "E-Mail Template"
        verbose_name_plural = "E-Mail Templates"
        unique_together = ['email_type', 'is_default']  # Only one default per email type

    def __str__(self):
        default_marker = " (Standard)" if self.is_default else ""
        recipient_marker = f" → {self.get_recipient_type_display()}"
        return f"{self.get_email_type_display()} - {self.name}{recipient_marker}{default_marker}"
    
    def get_variables_list(self):
        """Get list of available variables for this email type"""
        base_variables = [
            '{{salon_name}}', '{{salon_phone}}', '{{salon_address}}', 
            '{{salon_email}}', '{{current_date}}', '{{current_year}}'
        ]
        
        if self.email_type in ['appointment_confirmation', 'appointment_cancellation', 'appointment_reminder']:
            appointment_variables = [
                '{{customer_name}}', '{{customer_email}}', '{{customer_phone}}',
                '{{appointment_date}}', '{{appointment_time}}', '{{appointment_services}}',
                '{{services_count}}', '{{total_price}}', '{{total_duration}}', 
                '{{staff_name}}', '{{appointment_notes}}'
            ]
            
            # Service loop variables
            service_variables = [
                '--- Chi tiết Services (Loop) ---',
                '{% for service in services_details %}',
                '  {{service.name}} - Tên service',
                '  {{service.price}} € - Giá service', 
                '  {{service.duration}} phút - Thời gian',
                '  {{service.category}} - Danh mục',
                '  {{service.description}} - Mô tả',
                '{% endfor %}'
            ]
            
            return base_variables + appointment_variables + service_variables
        
        elif self.email_type in ['welcome_email', 'birthday_greeting', 'follow_up']:
            customer_variables = [
                '{{customer_name}}', '{{customer_email}}', '{{customer_phone}}'
            ]
            return base_variables + customer_variables
        
        elif self.email_type == 'admin_notification':
            admin_variables = [
                '{{customer_name}}', '{{customer_email}}', '{{appointment_details}}',
                '{{notification_type}}', '{{admin_name}}'
            ]
            return base_variables + admin_variables
        
        return base_variables
    
    def render_content(self, context=None):
        """Render template content with provided context"""
        if context is None:
            context = {}
        
        # Import Django Template here to avoid circular imports
        from django.template import Template, Context
        
        # Add default salon context
        default_context = {
            'salon_name': 'LK Nails & Lashes',
            'salon_phone': '+49 30 804997-18',
            'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
            'salon_email': 'lk.nails.lashes@gmail.com',
            'current_date': datetime.now().strftime('%d.%m.%Y'),
            'current_year': datetime.now().year,
        }
        
        # Merge contexts
        full_context = {**default_context, **context}
        
        # Use Django Template for proper rendering
        try:
            subject_template = Template(self.subject)
            html_template = Template(self.html_content)
            text_template = Template(self.text_content)
            
            django_context = Context(full_context)
            
            rendered_subject = subject_template.render(django_context)
            rendered_html = html_template.render(django_context)
            rendered_text = text_template.render(django_context)
            
            return {
                'subject': rendered_subject,
                'html_content': rendered_html,
                'text_content': rendered_text
            }
        except Exception as e:
            # Fallback to simple string replacement if Django template fails
            rendered_subject = self.subject
            rendered_html = self.html_content
            rendered_text = self.text_content
            
            for key, value in full_context.items():
                placeholder = f'{{{{{key}}}}}'
                rendered_subject = rendered_subject.replace(placeholder, str(value))
                rendered_html = rendered_html.replace(placeholder, str(value))
                rendered_text = rendered_text.replace(placeholder, str(value))
            
            return {
                'subject': rendered_subject,
                'html_content': rendered_html,
                'text_content': rendered_text
            }
    
    def save(self, *args, **kwargs):
        # Update available variables
        self.available_variables = '\n'.join(self.get_variables_list())
        
        # If this is set as default, unset other defaults for same email type
        if self.is_default:
            EmailTemplate.objects.filter(
                email_type=self.email_type, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        
        super().save(*args, **kwargs)


class DiscountCode(models.Model):
    DISCOUNT_TYPES = [
        ('first_time', 'Đăng ký lần đầu'),
        ('birthday', 'Sinh nhật'),
        ('event', 'Sự kiện đặc biệt'),
        ('vip', 'Khách VIP'),
        ('referral', 'Giới thiệu bạn bè'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('used', 'Đã sử dụng'),
        ('expired', 'Đã hết hạn'),
        ('disabled', 'Vô hiệu hóa'),
    ]
    
    code = models.CharField(max_length=20, unique=True, help_text="Mã giảm giá")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, help_text="Loại giảm giá")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Phần trăm giảm giá")
    max_discount_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Số tiền giảm tối đa")
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Giá trị đơn hàng tối thiểu")
    
    # User associations
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True, help_text="Khách hàng được cấp mã")
    email = models.EmailField(help_text="Email nhận mã giảm giá")
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0, help_text="Số lần đã sử dụng")
    max_usage = models.PositiveIntegerField(default=1, help_text="Số lần sử dụng tối đa")
    
    # Time constraints
    valid_from = models.DateTimeField(help_text="Có hiệu lực từ")
    valid_until = models.DateTimeField(help_text="Có hiệu lực đến")
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, help_text="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Mã giảm giá"
    
    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% ({self.get_discount_type_display()})"
    
    def is_valid(self):
        """Check if discount code is still valid"""
        from django.utils import timezone
        now = timezone.now()
        
        return (
            self.status == 'active' and
            self.valid_from <= now <= self.valid_until and
            self.usage_count < self.max_usage
        )
    
    def can_use(self, order_amount):
        """Check if discount can be applied to order amount"""
        return self.is_valid() and order_amount >= self.min_order_amount
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount for given order"""
        if not self.can_use(order_amount):
            return 0
        
        discount = (order_amount * self.discount_percentage / 100)
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
            
        return discount
    
    def use_code(self):
        """Mark code as used"""
        if self.is_valid():
            self.usage_count += 1
            if self.usage_count >= self.max_usage:
                self.status = 'used'
            self.save()
            return True
        return False
    
    @staticmethod
    def generate_code(prefix="LK", length=8):
        """Generate unique discount code"""
        import random
        import string
        
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length-len(prefix)))
            code = f"{prefix}{suffix}"
            if not DiscountCode.objects.filter(code=code).exists():
                return code


class DiscountSettings(models.Model):
    """Settings for automatic discount generation"""
    
    # First time customer discount
    first_time_enabled = models.BooleanField(default=True, help_text="Bật mã giảm giá cho khách mới")
    first_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5, help_text="% giảm giá khách mới")
    first_time_max_amount = models.DecimalField(max_digits=8, decimal_places=2, default=20, help_text="Số tiền giảm tối đa khách mới")
    first_time_min_order = models.DecimalField(max_digits=8, decimal_places=2, default=50, help_text="Đơn hàng tối thiểu khách mới")
    first_time_validity_days = models.PositiveIntegerField(default=30, help_text="Số ngày hiệu lực khách mới")
    
    # Birthday discount
    birthday_enabled = models.BooleanField(default=True, help_text="Bật mã giảm giá sinh nhật")
    birthday_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5, help_text="% giảm giá sinh nhật")
    birthday_max_amount = models.DecimalField(max_digits=8, decimal_places=2, default=25, help_text="Số tiền giảm tối đa sinh nhật")
    birthday_min_order = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Đơn hàng tối thiểu sinh nhật")
    birthday_validity_days = models.PositiveIntegerField(default=7, help_text="Số ngày hiệu lực sinh nhật")
    birthday_days_before = models.PositiveIntegerField(default=3, help_text="Gửi mã trước sinh nhật bao nhiêu ngày")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cài đặt mã giảm giá"
        verbose_name_plural = "Cài đặt mã giảm giá"
    
    def __str__(self):
        return f"Cài đặt mã giảm giá - Cập nhật: {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def get_current_settings(cls):
        """Get current discount settings, create if doesn't exist"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class SalonSettings(models.Model):
    """Single model to store salon configuration settings"""
    
    # Booking settings
    time_slot_interval_minutes = models.PositiveIntegerField(
        default=15, 
        help_text="Zeitintervall zwischen Terminen in Minuten",
        validators=[MinValueValidator(5), MaxValueValidator(60)]
    )
    
    # Business hours
    opening_time = models.TimeField(default=time(9, 0), help_text="Öffnungszeit")
    closing_time = models.TimeField(default=time(18, 0), help_text="Schließzeit")
    
    # Staff and booking limits
    max_concurrent_appointments = models.PositiveIntegerField(
        default=3, 
        help_text="Maximale Anzahl gleichzeitiger Termine (Anzahl Mitarbeiter)"
    )
    
    # Advance booking settings
    min_advance_booking_hours = models.PositiveIntegerField(
        default=2, 
        help_text="Mindestvorlaufzeit für Buchungen in Stunden"
    )
    max_advance_booking_days = models.PositiveIntegerField(
        default=90, 
        help_text="Maximaler Vorlauf für Buchungen in Tagen"
    )
    
    # Buffer times
    buffer_time_minutes = models.PositiveIntegerField(
        default=5, 
        help_text="Pufferzeit zwischen Terminen in Minuten"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Salon Einstellungen"
        verbose_name_plural = "Salon Einstellungen"

    def __str__(self):
        return f"Salon Einstellungen (Zeitintervall: {self.time_slot_interval_minutes} Min)"
    
    @classmethod
    def get_current_settings(cls):
        """Get the current salon settings (create if doesn't exist)"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'time_slot_interval_minutes': 15,
                'opening_time': time(9, 0),
                'closing_time': time(18, 0),
                'max_concurrent_appointments': 3,
                'min_advance_booking_hours': 2,
                'max_advance_booking_days': 90,
                'buffer_time_minutes': 5,
            }
        )
        return settings
    
    def get_available_time_slots(self, date, total_duration_minutes):
        """Generate available time slots for a given date and service duration"""
        from datetime import datetime, timedelta
        
        slots = []
        current_time = datetime.combine(date, self.opening_time)
        end_time = datetime.combine(date, self.closing_time)
        
        # Subtract service duration to ensure appointment can be completed within business hours
        latest_start = end_time - timedelta(minutes=total_duration_minutes)
        
        while current_time <= latest_start:
            slots.append(current_time.time())
            current_time += timedelta(minutes=self.time_slot_interval_minutes)
        
        return slots