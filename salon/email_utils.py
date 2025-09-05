from django.core.mail import get_connection, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import EmailConfiguration, EmailLog, EmailTemplate


def get_email_template(email_type):
    """Get the default email template for the given type"""
    try:
        return EmailTemplate.objects.filter(
            email_type=email_type, 
            is_active=True, 
            is_default=True
        ).first()
    except EmailTemplate.DoesNotExist:
        return None


def render_email_with_template(email_type, context):
    """Render email using EmailTemplate model"""
    template = get_email_template(email_type)
    if not template:
        # Fallback to hardcoded templates if no template found
        return None, None
    
    rendered = template.render_content(context)
    return rendered['subject'], rendered['html_content']


def create_email_log(recipient_email, recipient_name, sender_email, subject, 
                    email_type, appointment=None, customer=None, 
                    message_content="", full_message=""):
    """Create an email log entry"""
    return EmailLog.objects.create(
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        sender_email=sender_email,
        subject=subject,
        email_type=email_type,
        appointment=appointment,
        customer=customer,
        message_preview=message_content[:500] if message_content else "",
        full_message=full_message,
        status='pending'
    )


def send_tracked_email(recipient_email, recipient_name, subject, html_message, 
                      email_type, appointment=None, customer=None):
    """Send an email and track it in EmailLog"""
    try:
        email_config = EmailConfiguration.objects.filter(is_active=True).first()
        if not email_config:
            return False, "Keine E-Mail-Konfiguration aktiv"
            
        # Create email log entry
        plain_message = strip_tags(html_message)
        email_log = create_email_log(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            sender_email=email_config.from_email,
            subject=subject,
            email_type=email_type,
            appointment=appointment,
            customer=customer,
            message_content=plain_message,
            full_message=html_message
        )
        
        # Configure email connection
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=email_config.smtp_server,
            port=email_config.smtp_port,
            username=email_config.smtp_username,
            password=email_config.smtp_password,
            use_tls=email_config.use_tls,
        )
        
        # Send email
        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=email_config.from_email,
            to=[recipient_email],
            connection=connection,
        )
        email_message.content_subtype = "html"
        email_message.send()
        
        # Update log as sent
        email_log.status = 'sent'
        email_log.sent_at = timezone.now()
        email_log.save()
        
        return True, "E-Mail erfolgreich gesendet"
        
    except Exception as e:
        # Update log as failed
        if 'email_log' in locals():
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
        return False, f"E-Mail-Fehler: {str(e)}"


def send_appointment_email_tracked(appointment, email_type='confirmation'):
    """Send appointment emails with full tracking using EmailTemplate system"""
    try:
        email_config = EmailConfiguration.objects.filter(is_active=True).first()
        if not email_config:
            return False
        
        # Build context for template rendering
        services_list = [str(service) for service in appointment.services.all()]
        
        # Get detailed service information
        appointment_services = appointment.appointment_services.all()
        services_details = []
        for app_service in appointment_services:
            services_details.append({
                'name': app_service.service.name,
                'price': f"{app_service.price_at_booking:.2f}",
                'duration': f"{app_service.duration_at_booking}",
                'category': app_service.service.category.name if app_service.service.category else '',
                'description': app_service.service.description or ''
            })
        
        context = {
            'customer_name': appointment.customer.user.get_full_name(),
            'customer_email': appointment.customer.user.email,
            'customer_phone': appointment.customer.phone or '',
            'appointment_date': appointment.date.strftime('%d.%m.%Y'),
            'appointment_time': appointment.time.strftime('%H:%M'),
            'appointment_services': ', '.join(services_list),
            'services_details': services_details,  # Detailed service information
            'services_count': len(services_details),
            'total_price': f"{appointment.total_price:.2f}",
            'total_duration': f"{appointment.total_duration} Minuten",
            'staff_name': appointment.staff.user.get_full_name() if appointment.staff else 'Unser Team',
            'appointment_notes': appointment.notes or '',
            'salon_name': 'LK Nails & Lashes',
            'salon_phone': '+49 30 804997-18',
            'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
        }
        
        # Map email types to EmailTemplate types
        email_type_mapping = {
            'confirmation': 'appointment_confirmation',
            'cancellation': 'appointment_cancellation',
            'reminder': 'appointment_reminder',
        }
        
        template_type = email_type_mapping.get(email_type)
        if not template_type:
            return False
        
        success_count = 0
        
        # Send customer email using template
        subject, html_message = render_email_with_template(template_type, context)
        
        # Fallback to hardcoded template if no template found
        if not subject or not html_message:
            if email_type == 'confirmation':
                subject = f'Terminbestätigung - LK Nails & Lashes'
                html_message = render_to_string('emails/appointment_confirmation.html', {
                    'appointment': appointment,
                    'customer': appointment.customer,
                    'services': appointment.services.all(),
                    'total_price': appointment.total_price,
                    'total_duration': appointment.total_duration,
                    'salon_name': 'LK Nails & Lashes',
                    'salon_phone': '+49 30 804997-18',
                    'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
                })
            elif email_type == 'cancellation':
                subject = f'Terminabsage - LK Nails & Lashes'
                html_message = render_to_string('emails/appointment_cancellation.html', {
                    'appointment': appointment,
                    'customer': appointment.customer,
                    'services': appointment.services.all(),
                    'total_price': appointment.total_price,
                    'total_duration': appointment.total_duration,
                    'salon_name': 'LK Nails & Lashes',
                    'salon_phone': '+49 30 804997-18',
                    'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
                })
            else:
                return False
        
        # Send to customer
        success, message = send_tracked_email(
            recipient_email=appointment.customer.user.email,
            recipient_name=appointment.customer.user.get_full_name(),
            subject=subject,
            html_message=html_message,
            email_type=template_type,
            appointment=appointment,
            customer=appointment.customer
        )
        
        if success:
            success_count += 1
        
        # Send admin notification using template
        admin_context = context.copy()
        admin_context.update({
            'notification_type': 'Neue Buchung' if email_type == 'confirmation' else 'Terminabsage',
            'admin_name': 'Admin'
        })
        
        admin_subject, admin_html = render_email_with_template('admin_notification', admin_context)
        
        # Fallback to hardcoded admin template if no template found
        if not admin_subject or not admin_html:
            if email_type == 'confirmation':
                admin_subject = f'Neue Terminbuchung - {appointment.customer.user.get_full_name()}'
                admin_html = render_to_string('emails/admin_appointment_notification.html', {
                    'appointment': appointment,
                    'customer': appointment.customer,
                    'services': appointment.services.all(),
                    'total_price': appointment.total_price,
                    'total_duration': appointment.total_duration,
                    'salon_name': 'LK Nails & Lashes',
                    'salon_phone': '+49 30 804997-18',
                    'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
                    'is_admin_email': True
                })
            elif email_type == 'cancellation':
                admin_subject = f'Terminabsage - {appointment.customer.user.get_full_name()}'
                admin_html = render_to_string('emails/admin_cancellation_notification.html', {
                    'appointment': appointment,
                    'customer': appointment.customer,
                    'services': appointment.services.all(),
                    'total_price': appointment.total_price,
                    'total_duration': appointment.total_duration,
                    'salon_name': 'LK Nails & Lashes',
                    'salon_phone': '+49 30 804997-18',
                    'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
                    'is_admin_email': True
                })
            else:
                return success_count > 0
        
        # Send to admin
        admin_success, admin_message = send_tracked_email(
            recipient_email=email_config.admin_email,
            recipient_name="Admin",
            subject=admin_subject,
            html_message=admin_html,
            email_type='admin_notification',
            appointment=appointment,
            customer=appointment.customer
        )
        
        if admin_success:
            success_count += 1
        
        return success_count > 0
        
    except Exception as e:
        print(f"Email sending error: {e}")
        return False