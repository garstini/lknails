from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import get_connection, EmailMessage
from datetime import datetime, timedelta
import json
from .models import (
    Appointment, Service, Customer, Staff, BlogPost, 
    Gallery, Review, BusinessHours, EmailConfiguration
)


@staff_member_required
def admin_dashboard(request):
    # Date ranges
    today = timezone.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Basic stats
    total_customers = Customer.objects.count()
    total_appointments = Appointment.objects.count()
    total_services = Service.objects.filter(is_active=True).count()
    total_staff = Staff.objects.filter(is_available=True).count()
    
    # Today's appointments
    todays_appointments = Appointment.objects.filter(
        date=today,
        status__in=['confirmed', 'pending']
    ).select_related('customer__user', 'staff__user').order_by('time')
    
    # This week's stats
    this_week_appointments = Appointment.objects.filter(
        date__gte=this_week_start,
        date__lte=today
    ).count()
    
    # Revenue stats
    this_month_revenue = Appointment.objects.filter(
        date__gte=this_month_start,
        status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    last_month_revenue = Appointment.objects.filter(
        date__gte=last_month_start,
        date__lt=this_month_start,
        status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Popular services
    popular_services = Service.objects.annotate(
        booking_count=Count('appointmentservice')
    ).order_by('-booking_count')[:5]
    
    # Recent reviews
    recent_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('customer__user', 'service').order_by('-created_at')[:5]
    
    # Staff performance
    staff_performance = Staff.objects.annotate(
        appointments_count=Count('appointments', 
                               filter=Q(appointments__date__gte=this_month_start))
    ).order_by('-appointments_count')
    
    # Appointment status distribution
    appointment_status = Appointment.objects.filter(
        date__gte=this_month_start
    ).values('status').annotate(count=Count('id'))
    
    # Monthly appointment trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_start = (this_month_start - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        month_appointments = Appointment.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).count()
        
        monthly_trends.append({
            'month': month_start.strftime('%B %Y'),
            'appointments': month_appointments,
            'chart_height': max(month_appointments * 3, 10)  # Minimum height of 10px
        })
    
    monthly_trends.reverse()
    
    # Pending approvals
    pending_reviews = Review.objects.filter(is_approved=False).count()
    unpublished_posts = BlogPost.objects.filter(is_published=False).count()
    
    context = {
        'total_customers': total_customers,
        'total_appointments': total_appointments,
        'total_services': total_services,
        'total_staff': total_staff,
        'todays_appointments': todays_appointments,
        'this_week_appointments': this_week_appointments,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'popular_services': popular_services,
        'recent_reviews': recent_reviews,
        'staff_performance': staff_performance,
        'appointment_status': appointment_status,
        'monthly_trends': monthly_trends,
        'pending_reviews': pending_reviews,
        'unpublished_posts': unpublished_posts,
        'today': today,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def business_hours_config(request):
    business_hours = BusinessHours.objects.all().order_by('day_of_week')
    
    # Create default business hours if none exist
    if not business_hours.exists():
        days = [
            (0, 'Montag', True, '09:30', '19:00'),
            (1, 'Dienstag', True, '09:30', '19:00'), 
            (2, 'Mittwoch', True, '09:30', '19:00'),
            (3, 'Donnerstag', True, '09:30', '19:00'),
            (4, 'Freitag', True, '09:30', '19:00'),
            (5, 'Samstag', True, '10:00', '17:00'),
            (6, 'Sonntag', False, '09:30', '19:00'),
        ]
        
        for day_num, day_name, is_open, open_time, close_time in days:
            BusinessHours.objects.create(
                day_of_week=day_num,
                is_open=is_open,
                opening_time=datetime.strptime(open_time, '%H:%M').time(),
                closing_time=datetime.strptime(close_time, '%H:%M').time()
            )
        
        business_hours = BusinessHours.objects.all().order_by('day_of_week')
    
    # Handle POST request to save business hours
    if request.method == 'POST':
        from django.contrib import messages
        try:
            for day in range(7):  # 0-6 for Monday-Sunday
                is_open = request.POST.get(f'is_open_{day}') == 'on'
                opening_time = request.POST.get(f'opening_time_{day}')
                closing_time = request.POST.get(f'closing_time_{day}')
                break_start = request.POST.get(f'break_start_{day}')
                break_end = request.POST.get(f'break_end_{day}')
                
                # Get or create business hour entry
                business_hour, created = BusinessHours.objects.get_or_create(
                    day_of_week=day,
                    defaults={
                        'is_open': is_open,
                        'opening_time': datetime.strptime(opening_time or '09:00', '%H:%M').time(),
                        'closing_time': datetime.strptime(closing_time or '18:00', '%H:%M').time(),
                    }
                )
                
                # Update fields
                business_hour.is_open = is_open
                if opening_time:
                    business_hour.opening_time = datetime.strptime(opening_time, '%H:%M').time()
                if closing_time:
                    business_hour.closing_time = datetime.strptime(closing_time, '%H:%M').time()
                if break_start:
                    business_hour.break_start = datetime.strptime(break_start, '%H:%M').time()
                else:
                    business_hour.break_start = None
                if break_end:
                    business_hour.break_end = datetime.strptime(break_end, '%H:%M').time()
                else:
                    business_hour.break_end = None
                    
                business_hour.save()
            
            messages.success(request, 'Öffnungszeiten wurden erfolgreich gespeichert!')
            
        except Exception as e:
            messages.error(request, f'Fehler beim Speichern: {str(e)}')
            
        # Refresh data after update
        business_hours = BusinessHours.objects.all().order_by('day_of_week')
    
    context = {
        'business_hours': business_hours,
    }
    
    return render(request, 'admin/business_hours.html', context)


@staff_member_required  
def email_config(request):
    email_configs = EmailConfiguration.objects.all()
    active_config = email_configs.filter(is_active=True).first()
    
    context = {
        'email_configs': email_configs,
        'active_config': active_config,
    }
    
    return render(request, 'admin/email_config.html', context)


@staff_member_required
@require_POST
def test_email(request, config_id):
    """Test email configuration by sending a test email"""
    try:
        config = EmailConfiguration.objects.get(id=config_id)
        
        # Test connection
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=config.smtp_server,
            port=config.smtp_port,
            username=config.smtp_username,
            password=config.smtp_password,
            use_tls=config.use_tls,
        )
        
        # Send test email
        test_email = EmailMessage(
            subject='Test E-Mail - LK Nails & Lashes',
            body=f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d4af37;">✅ Test E-Mail erfolgreich!</h2>
                <p>Diese Test-E-Mail wurde erfolgreich von der LK Nails & Lashes Admin-Konfiguration gesendet.</p>
                <hr>
                <h3>Konfigurationsdetails:</h3>
                <ul>
                    <li><strong>Konfigurationsname:</strong> {config.name}</li>
                    <li><strong>SMTP Server:</strong> {config.smtp_server}:{config.smtp_port}</li>
                    <li><strong>TLS:</strong> {'Aktiviert' if config.use_tls else 'Deaktiviert'}</li>
                    <li><strong>Von E-Mail:</strong> {config.from_email}</li>
                </ul>
                <hr>
                <p><small>Gesendet am: {datetime.now().strftime('%d.m.Y %H:%M:%S')}</small></p>
            </body>
            </html>
            """,
            from_email=config.from_email,
            to=[config.admin_email],
            connection=connection,
        )
        test_email.content_subtype = "html"
        test_email.send()
        
        return JsonResponse({'success': True, 'message': 'Test-E-Mail erfolgreich gesendet!'})
        
    except EmailConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'E-Mail-Konfiguration nicht gefunden'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_POST
def activate_email_config(request, config_id):
    """Activate an email configuration"""
    try:
        # Deactivate all configs first
        EmailConfiguration.objects.all().update(is_active=False)
        
        # Activate the selected config
        config = EmailConfiguration.objects.get(id=config_id)
        config.is_active = True
        config.save()
        
        return JsonResponse({'success': True})
        
    except EmailConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Konfiguration nicht gefunden'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})