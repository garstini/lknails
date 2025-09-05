from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, timedelta, date
import json

from .models import (
    Service, ServiceCategory, Appointment, BlogPost, 
    Gallery, Review, Staff, Customer, EmailConfiguration, EmailLog
)
from .email_utils import send_appointment_email_tracked
from .forms import (
    UserRegistrationForm, AppointmentForm, ServiceFilterForm,
    CustomerProfileForm, ReviewForm
)


def send_appointment_email(appointment, email_type='confirmation'):
    """Send email notifications for appointments"""
    try:
        email_config = EmailConfiguration.objects.filter(is_active=True).first()
        if not email_config:
            return False
            
        # Configure email settings
        from django.core.mail import get_connection
        from django.core.mail import EmailMessage
        
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=email_config.smtp_server,
            port=email_config.smtp_port,
            username=email_config.smtp_username,
            password=email_config.smtp_password,
            use_tls=email_config.use_tls,
        )
        
        # Email templates context
        context = {
            'appointment': appointment,
            'customer': appointment.customer,
            'services': appointment.services.all(),
            'total_price': appointment.total_price,
            'total_duration': appointment.total_duration,
            'salon_name': 'LK Nails & Lashes',
            'salon_phone': '+49 30 80499718',
            'salon_address': 'Hindenburgdamm 75, 12203 Berlin, Germany',
        }
        
        # Send confirmation email to customer
        if email_type == 'confirmation':
            subject = f'Terminbestätigung - LK Nails & Lashes'
            html_message = render_to_string('emails/appointment_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            customer_email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=email_config.from_email,
                to=[appointment.customer.user.email],
                connection=connection,
            )
            customer_email.content_subtype = "html"
            customer_email.send()
            
            # Send notification email to admin
            admin_subject = f'Neue Terminbuchung - {appointment.customer.user.get_full_name()}'
            admin_context = context.copy()
            admin_context['is_admin_email'] = True
            admin_html = render_to_string('emails/admin_appointment_notification.html', admin_context)
            
            admin_email = EmailMessage(
                subject=admin_subject,
                body=admin_html,
                from_email=email_config.from_email,
                to=[email_config.admin_email],
                connection=connection,
            )
            admin_email.content_subtype = "html"
            admin_email.send()
            
        elif email_type == 'cancellation':
            subject = f'Terminabsage - LK Nails & Lashes'
            html_message = render_to_string('emails/appointment_cancellation.html', context)
            
            customer_email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=email_config.from_email,
                to=[appointment.customer.user.email],
                connection=connection,
            )
            customer_email.content_subtype = "html"
            customer_email.send()
            
            # Notify admin about cancellation
            admin_subject = f'Terminabsage - {appointment.customer.user.get_full_name()}'
            admin_context = context.copy()
            admin_context['is_admin_email'] = True
            admin_html = render_to_string('emails/admin_cancellation_notification.html', admin_context)
            
            admin_email = EmailMessage(
                subject=admin_subject,
                body=admin_html,
                from_email=email_config.from_email,
                to=[email_config.admin_email],
                connection=connection,
            )
            admin_email.content_subtype = "html"
            admin_email.send()
            
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def home(request):
    featured_services = Service.objects.filter(is_active=True)[:6]
    recent_posts = BlogPost.objects.filter(is_published=True)[:3]
    # Only get gallery items that have images or allow empty ones for placeholder display
    featured_gallery = Gallery.objects.filter(is_featured=True)[:8]
    reviews = Review.objects.filter(is_approved=True)[:6]
    
    context = {
        'featured_services': featured_services,
        'recent_posts': recent_posts,
        'featured_gallery': featured_gallery,
        'reviews': reviews,
    }
    return render(request, 'salon/home.html', context)


def services(request):
    services_list = Service.objects.filter(is_active=True)
    categories = ServiceCategory.objects.all()
    
    form = ServiceFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['category']:
            services_list = services_list.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['price_min']:
            services_list = services_list.filter(price__gte=form.cleaned_data['price_min'])
        if form.cleaned_data['price_max']:
            services_list = services_list.filter(price__lte=form.cleaned_data['price_max'])
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        services_list = services_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(services_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
        'search_query': search_query,
    }
    return render(request, 'salon/services.html', context)


def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)
    related_services = Service.objects.filter(
        category=service.category, 
        is_active=True
    ).exclude(id=service_id)[:4]
    
    reviews = Review.objects.filter(service=service, is_approved=True)[:5]
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    
    context = {
        'service': service,
        'related_services': related_services,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'salon/service_detail.html', context)


@login_required
def book_appointment(request, service_id=None):
    service = None
    if service_id:
        service = get_object_or_404(Service, id=service_id, is_active=True)
    
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            from .models import SalonSettings
            from django.utils import timezone
            
            selected_services = form.cleaned_data['services']
            selected_date = form.cleaned_data['date']
            selected_time = form.cleaned_data['time']
            
            total_duration = sum(service.duration_minutes for service in selected_services)
            total_price = sum(service.price for service in selected_services)
            
            # Get salon settings for validation
            salon_settings = SalonSettings.get_current_settings()
            
            # Validate booking time constraints
            now = timezone.now()
            appointment_datetime = datetime.combine(selected_date, selected_time)
            time_until_appointment = (appointment_datetime - now.replace(tzinfo=None)).total_seconds() / 3600
            
            # Check minimum advance booking time
            if time_until_appointment < salon_settings.min_advance_booking_hours:
                messages.error(request, f'Termine müssen mindestens {salon_settings.min_advance_booking_hours} Stunden im Voraus gebucht werden.')
                form = AppointmentForm(request.POST)  # Keep form data
            # Check maximum advance booking time
            elif time_until_appointment > (salon_settings.max_advance_booking_days * 24):
                messages.error(request, f'Termine können maximal {salon_settings.max_advance_booking_days} Tage im Voraus gebucht werden.')
                form = AppointmentForm(request.POST)  # Keep form data
            else:
                # Find available staff for the appointment
                available_staff = get_available_staff(
                    selected_date, 
                    selected_time, 
                    total_duration
                )
                
                if available_staff:
                    # Create the appointment
                    appointment = form.save(commit=False)
                    appointment.customer = customer
                    appointment.staff = available_staff[0]  # Assign first available staff
                    appointment.total_duration = total_duration
                    appointment.total_price = total_price
                    # Automatically confirm the appointment
                    appointment.status = 'confirmed'
                    appointment.save()
                    
                    # Create AppointmentService entries
                    for service in selected_services:
                        from .models import AppointmentService
                        AppointmentService.objects.create(
                            appointment=appointment,
                            service=service,
                            price_at_booking=service.price,
                            duration_at_booking=service.duration_minutes
                        )
                
                    # Save many-to-many relationship
                    appointment.services.set(selected_services)
                    
                    # Send email notifications automatically
                    try:
                        # Send confirmation email to customer
                        send_appointment_email_tracked(appointment, 'confirmation')
                        messages.success(request, 'Ihr Termin wurde erfolgreich gebucht und automatisch bestätigt! Eine Bestätigungs-E-Mail wurde gesendet.')
                    except Exception as e:
                        # Even if email fails, appointment is still created
                        messages.success(request, 'Ihr Termin wurde erfolgreich gebucht und automatisch bestätigt!')
                        print(f'Email sending failed: {e}')  # Log error for debugging
                        
                    return redirect('appointment_confirmation', appointment_id=appointment.id)
                else:
                    # This should rarely happen now since API filters unavailable slots
                    messages.error(request, 'Der gewählte Zeitslot ist nicht mehr verfügbar. Bitte wählen Sie einen anderen Zeitpunkt.')
    else:
        initial_data = {}
        if service:
            initial_data['services'] = [service]
        form = AppointmentForm(initial=initial_data)
    
    # Get services for template (since form.services.queryset seems to be empty in template)
    services_by_category = {}
    for service_item in Service.objects.filter(is_active=True).select_related('category'):
        if service_item.category.name not in services_by_category:
            services_by_category[service_item.category.name] = []
        services_by_category[service_item.category.name].append(service_item)
    
    context = {
        'form': form,
        'service': service,
        'services_by_category': services_by_category,
        'all_services': Service.objects.filter(is_active=True),
    }
    return render(request, 'salon/book_appointment.html', context)


def get_available_staff(date, time, duration_minutes):
    from .models import SalonSettings
    
    appointment_datetime = datetime.combine(date, time)
    end_datetime = appointment_datetime + timedelta(minutes=duration_minutes)
    
    # Get salon settings for buffer time
    salon_settings = SalonSettings.get_current_settings()
    buffer_minutes = salon_settings.buffer_time_minutes
    
    # Add buffer time to the appointment window
    buffered_start = appointment_datetime - timedelta(minutes=buffer_minutes)
    buffered_end = end_datetime + timedelta(minutes=buffer_minutes)
    
    # Get all staff
    all_staff = Staff.objects.filter(is_available=True)
    available_staff = []
    
    for staff_member in all_staff:
        # Check if staff has conflicting appointments
        conflicting_appointments = Appointment.objects.filter(
            staff=staff_member,
            date=date,
            status__in=['confirmed', 'pending']
        )
        
        has_conflict = False
        for appointment in conflicting_appointments:
            existing_start = datetime.combine(appointment.date, appointment.time)
            # Use appointment total_duration if available, otherwise fallback to service duration
            existing_duration = appointment.total_duration if appointment.total_duration else (
                appointment.services.first().duration_minutes if appointment.services.exists() else 60
            )
            existing_end = existing_start + timedelta(minutes=existing_duration)
            
            # Add buffer time to existing appointment
            existing_buffered_start = existing_start - timedelta(minutes=buffer_minutes)
            existing_buffered_end = existing_end + timedelta(minutes=buffer_minutes)
            
            # Check for overlap with buffer time
            if buffered_start < existing_buffered_end and buffered_end > existing_buffered_start:
                has_conflict = True
                break
        
        if not has_conflict:
            available_staff.append(staff_member)
    
    return available_staff


def get_available_times_api(request):
    """API endpoint to get available time slots for a given date and duration"""
    from django.http import JsonResponse
    from datetime import datetime, timedelta
    from .models import SalonSettings, Appointment, Staff
    
    try:
        date_str = request.GET.get('date')
        total_duration = int(request.GET.get('total_duration', 0))
        
        if not date_str or not total_duration:
            return JsonResponse({'error': 'Date and total_duration are required'}, status=400)
        
        # Parse the date
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get salon settings
        salon_settings = SalonSettings.get_current_settings()
        
        # Generate all possible time slots
        all_slots = salon_settings.get_available_time_slots(selected_date, total_duration)
        
        # Filter out slots that don't have available staff
        available_slots = []
        for slot_time in all_slots:
            # Check if we have enough available staff for this time slot
            appointment_datetime = datetime.combine(selected_date, slot_time)
            end_datetime = appointment_datetime + timedelta(minutes=total_duration)
            
            # Add buffer time to match get_available_staff logic
            buffer_minutes = salon_settings.buffer_time_minutes
            buffered_start = appointment_datetime - timedelta(minutes=buffer_minutes)
            buffered_end = end_datetime + timedelta(minutes=buffer_minutes)
            
            # Count available staff at this time
            all_staff = Staff.objects.filter(is_available=True)
            available_staff_count = 0
            
            for staff_member in all_staff:
                # Check if staff has conflicting appointments
                conflicting_appointments = Appointment.objects.filter(
                    staff=staff_member,
                    date=selected_date,
                    status__in=['confirmed', 'pending']
                )
                
                has_conflict = False
                for appointment in conflicting_appointments:
                    existing_start = datetime.combine(appointment.date, appointment.time)
                    # Use appointment total_duration instead of service duration for better accuracy
                    if appointment.total_duration:
                        existing_duration = appointment.total_duration
                    elif appointment.services.exists():
                        existing_duration = appointment.services.first().duration_minutes
                    else:
                        existing_duration = 60  # Default fallback duration
                    existing_end = existing_start + timedelta(minutes=existing_duration)
                    
                    # Add buffer time to existing appointment to match get_available_staff logic
                    existing_buffered_start = existing_start - timedelta(minutes=buffer_minutes)
                    existing_buffered_end = existing_end + timedelta(minutes=buffer_minutes)
                    
                    # Check for overlap with buffer time
                    if buffered_start < existing_buffered_end and buffered_end > existing_buffered_start:
                        has_conflict = True
                        break
                
                if not has_conflict:
                    available_staff_count += 1
            
            # If we have at least one available staff member, include this slot
            if available_staff_count > 0:
                available_slots.append(slot_time.strftime('%H:%M'))
        
        return JsonResponse({
            'available_times': available_slots,
            'total_slots_generated': len(all_slots),
            'available_slots': len(available_slots),
            'settings': {
                'interval_minutes': salon_settings.time_slot_interval_minutes,
                'opening_time': salon_settings.opening_time.strftime('%H:%M'),
                'closing_time': salon_settings.closing_time.strftime('%H:%M'),
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        customer__user=request.user
    )
    return render(request, 'salon/appointment_confirmation.html', {'appointment': appointment})


@login_required
def my_appointments(request):
    customer = get_object_or_404(Customer, user=request.user)
    appointments = Appointment.objects.filter(customer=customer).order_by('-date', '-time')
    
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'salon/my_appointments.html', {'page_obj': page_obj})


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        customer__user=request.user
    )
    
    # Only allow cancellation if appointment is at least 1 hour away
    appointment_datetime = timezone.make_aware(datetime.combine(appointment.date, appointment.time))
    if appointment_datetime - timedelta(hours=1) > timezone.now():
        appointment.status = 'cancelled'
        appointment.save()
        
        # Send cancellation email notifications
        if send_appointment_email_tracked(appointment, 'cancellation'):
            messages.success(request, 'Ihr Termin wurde storniert. Eine Bestätigungs-E-Mail wurde gesendet.')
        else:
            messages.success(request, 'Ihr Termin wurde storniert.')
    else:
        messages.error(request, 'Termine können nur mindestens 1 Stunde im Voraus storniert werden.')
    
    return redirect('my_appointments')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=customer, user=request.user)
    
    return render(request, 'salon/profile.html', {'form': form})


def blog(request):
    posts = BlogPost.objects.filter(is_published=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'salon/blog.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'salon/blog_detail.html', context)


def gallery(request):
    gallery_items = Gallery.objects.all().order_by('-created_at')
    
    # Filter by service category
    category_id = request.GET.get('category')
    if category_id:
        gallery_items = gallery_items.filter(service__category_id=category_id)
    
    categories = ServiceCategory.objects.all()
    
    paginator = Paginator(gallery_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    featured_count = Gallery.objects.filter(is_featured=True).count()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'featured_count': featured_count,
    }
    return render(request, 'salon/gallery.html', context)


def about(request):
    staff_members = Staff.objects.filter(is_available=True)
    return render(request, 'salon/about.html', {'staff_members': staff_members})


def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'salon/contact.html')


def get_available_times(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        service_id = request.GET.get('service_id')
        
        if not date_str or not service_id:
            return JsonResponse({'error': 'Date and service_id are required'}, status=400)
        
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.objects.get(id=service_id)
        except (ValueError, Service.DoesNotExist):
            return JsonResponse({'error': 'Invalid date or service'}, status=400)
        
        # Generate time slots (9 AM to 6 PM, 15-minute intervals)
        available_times = []
        start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9))
        end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=18))
        
        current_time = start_time
        while current_time < end_time:
            # Check how many appointments are already booked at this time
            appointments_count = Appointment.objects.filter(
                date=selected_date,
                time=current_time.time(),
                status__in=['confirmed', 'pending']
            ).count()
            
            # If less than 3 staff are booked, time slot is available
            if appointments_count < 3:
                available_times.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=15)
        
        return JsonResponse({'available_times': available_times})
    
    return JsonResponse({'error': 'Only GET method allowed'}, status=405)


@login_required 
def email_history(request):
    """Show email history for the logged-in customer"""
    try:
        customer = Customer.objects.get(user=request.user)
        
        # Get all emails sent to this customer
        emails = EmailLog.objects.filter(
            customer=customer
        ).select_related('appointment').order_by('-created_at')
        
        # Paginate emails
        paginator = Paginator(emails, 10)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        
        context = {
            'page_obj': page_obj,
            'customer': customer,
        }
        return render(request, 'salon/email_history.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'Kundendaten nicht gefunden.')
        return redirect('home')


@login_required
def leave_review(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if user owns this appointment
        if appointment.customer.user != request.user:
            messages.error(request, 'Sie sind nicht berechtigt, eine Bewertung für diesen Termin abzugeben.')
            return redirect('my_appointments')
            
        # Check if appointment is completed
        if appointment.status != 'completed':
            messages.error(request, 'Sie können nur abgeschlossene Termine bewerten.')
            return redirect('my_appointments')
            
        # Check if review already exists
        if hasattr(appointment, 'review'):
            messages.info(request, 'Sie haben diesen Termin bereits bewertet.')
            return redirect('my_appointments')
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.customer = appointment.customer
                review.appointment = appointment
                
                # Get the main service from appointment
                if appointment.services.exists():
                    review.service = appointment.services.first()
                    
                review.staff = appointment.staff
                review.save()
                
                messages.success(request, 'Vielen Dank für Ihre Bewertung!')
                return redirect('my_appointments')
        else:
            form = ReviewForm()
        
        context = {
            'form': form,
            'appointment': appointment,
            'services': appointment.services.all(),
        }
        return render(request, 'salon/leave_review.html', context)
        
    except Exception as e:
        messages.error(request, 'Es gab ein Problem beim Laden der Bewertungsseite.')
        return redirect('my_appointments')


def reviews_list(request):
    reviews = Review.objects.filter(is_approved=True).select_related(
        'customer__user', 'service', 'staff__user'
    ).order_by('-created_at')
    
    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        reviews = reviews.filter(service_id=service_id)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reviews, 12)  # 12 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured reviews
    featured_reviews = Review.objects.filter(
        is_approved=True, is_featured=True
    ).select_related('customer__user', 'service').order_by('-created_at')[:3]
    
    # Calculate average rating
    from django.db.models import Avg
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Get services for filter dropdown
    services = Service.objects.filter(is_active=True)
    
    context = {
        'reviews': page_obj,
        'featured_reviews': featured_reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count(),
        'services': services,
        'selected_service': int(service_id) if service_id else None,
    }
    return render(request, 'salon/reviews.html', context)


def service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)
    reviews = Review.objects.filter(
        service=service, is_approved=True
    ).select_related('customer__user', 'staff__user').order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'service': service,
        'reviews': page_obj,
        'avg_rating': service.get_average_rating(),
        'review_count': service.get_review_count(),
    }
    return render(request, 'salon/service_reviews.html', context)