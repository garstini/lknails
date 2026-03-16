from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import Context, Template
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from bookings.models import Booking, BookingItem
from core.email_utils import send_configured_email
from core.models import SiteSettings, WorkingHour
from services.models import Service


class BookingForm(forms.Form):
    customer_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=32)
    email = forms.EmailField()
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time", "step": 900}))
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["services"].queryset = Service.objects.filter(is_active=True).order_by("category", "subcategory", "name")
        self.fields["customer_name"].widget.attrs.update({"placeholder": "Anna Mustermann"})
        self.fields["phone"].widget.attrs.update({"placeholder": "+49 ..."})
        self.fields["email"].widget.attrs.update({"placeholder": "name@example.com"})
        self.fields["appointment_date"].widget.attrs.update({"min": timezone.localdate().isoformat()})


class TestEmailForm(forms.Form):
    recipient = forms.EmailField()


def get_site_settings():
    return SiteSettings.objects.first() or SiteSettings(
        booking_slot_minutes=15,
        concurrent_capacity=3,
        timezone="Europe/Berlin",
        site_name="LK Nails & Lashes",
        domain="lknailslashes.de",
    )


def get_booking_timezone():
    return ZoneInfo(get_site_settings().timezone or settings.TIME_ZONE)


def combine_local_datetime(appointment_date, appointment_time):
    combined = datetime.combine(appointment_date, appointment_time)
    return timezone.make_aware(combined, get_booking_timezone())


def calculate_totals(services):
    total_duration = sum(service.duration_minutes for service in services)
    total_price = sum((service.current_price for service in services), start=Decimal("0.00"))
    return total_duration, total_price


def get_available_slots(target_date):
    site_settings = get_site_settings()
    working_hour = get_working_hour(target_date)
    if not working_hour:
        return []

    tz = get_booking_timezone()
    day_start = timezone.make_aware(datetime.combine(target_date, working_hour.open_time), tz)
    day_end = timezone.make_aware(datetime.combine(target_date, working_hour.close_time), tz)
    slot_minutes = site_settings.booking_slot_minutes

    slots = []
    current = day_start
    while current + timedelta(minutes=slot_minutes) <= day_end:
        slots.append(current)
        current += timedelta(minutes=slot_minutes)
    return slots


def get_available_start_slots(target_date, duration_minutes):
    if duration_minutes <= 0:
        return []

    working_hour = get_working_hour(target_date)
    if not working_hour:
        return []

    tz = get_booking_timezone()
    day_end = timezone.make_aware(datetime.combine(target_date, working_hour.close_time), tz)
    valid_slots = []
    for slot in get_available_slots(target_date):
        if slot + timedelta(minutes=duration_minutes) > day_end:
            continue
        if is_booking_available(slot, duration_minutes):
            valid_slots.append(slot)
    return valid_slots


def get_working_hour(target_date):
    return WorkingHour.objects.filter(weekday=target_date.weekday(), is_open=True).first()


def is_booking_available(starts_at, duration_minutes):
    site_settings = get_site_settings()
    ends_at = starts_at + timedelta(minutes=duration_minutes)
    slot_minutes = site_settings.booking_slot_minutes
    overlapping = Booking.objects.filter(
        ~Q(status=Booking.Status.CANCELLED),
        starts_at__lt=ends_at,
        ends_at__gt=starts_at,
    ).only("starts_at", "ends_at")
    current = starts_at
    while current < ends_at:
        slot_end = current + timedelta(minutes=slot_minutes)
        slot_count = sum(1 for booking in overlapping if booking.starts_at < slot_end and booking.ends_at > current)
        if slot_count >= site_settings.concurrent_capacity:
            return False
        current = slot_end
    return True


def render_email_template(template_type, fallback_subject, fallback_body, context):
    email_template = SiteSettings.objects.none()
    from core.models import EmailTemplate

    email_template = EmailTemplate.objects.filter(template_type=template_type).first()
    if not email_template:
        return fallback_subject, fallback_body
    template_context = Context(context)
    subject = Template(email_template.subject).render(template_context).strip()
    body = Template(email_template.body).render(template_context).strip()
    return subject or fallback_subject, body or fallback_body


class BookingCreateView(FormView):
    template_name = "bookings/booking_form.html"
    form_class = BookingForm
    success_url = reverse_lazy("booking_success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.filter(is_active=True).order_by("category", "subcategory", "name")
        grouped = defaultdict(lambda: defaultdict(list))
        selected_service_ids = set()
        if self.request.method == "POST":
            selected_service_ids = {int(service_id) for service_id in self.request.POST.getlist("services") if service_id.isdigit()}
        for service in services:
            grouped[service.category][service.subcategory].append(service)
        context["grouped_services"] = {
            category: dict(subcategories)
            for category, subcategories in grouped.items()
        }
        context["site_settings"] = get_site_settings()
        context["selected_service_ids"] = selected_service_ids
        context["service_categories"] = list(context["grouped_services"].keys())
        return context

    def form_valid(self, form):
        selected_services = list(form.cleaned_data["services"])
        total_duration, total_price = calculate_totals(selected_services)
        starts_at = combine_local_datetime(
            form.cleaned_data["appointment_date"],
            form.cleaned_data["appointment_time"],
        )

        if not total_duration:
            form.add_error("services", _("Please select at least one service."))
            return self.form_invalid(form)

        if starts_at < timezone.now():
            form.add_error("appointment_date", _("Please select a future appointment time."))
            return self.form_invalid(form)

        working_hour = get_working_hour(starts_at.date())
        if not working_hour:
            form.add_error("appointment_date", _("The salon is closed on this day."))
            return self.form_invalid(form)

        closing_at = timezone.make_aware(datetime.combine(starts_at.date(), working_hour.close_time), get_booking_timezone())
        if starts_at + timedelta(minutes=total_duration) > closing_at:
            form.add_error("appointment_time", _("Selected services do not fit into working hours."))
            return self.form_invalid(form)

        if not is_booking_available(starts_at, total_duration):
            form.add_error("appointment_time", _("This time slot is fully booked. Please choose another time."))
            return self.form_invalid(form)

        with transaction.atomic():
            booking = Booking.objects.create(
                customer_name=form.cleaned_data["customer_name"],
                phone=form.cleaned_data["phone"],
                email=form.cleaned_data["email"],
                note=form.cleaned_data["note"],
                starts_at=starts_at,
                total_duration_minutes=total_duration,
                total_price=total_price,
            )
            for service in selected_services:
                BookingItem.objects.create(
                    booking=booking,
                    service=service,
                    category=service.category,
                    subcategory=service.subcategory,
                    service_name=service.name,
                    duration_minutes=service.duration_minutes,
                    price=service.current_price,
                )
                Service.objects.filter(pk=service.pk).update(booking_count=service.booking_count + 1)
            booking.recalculate()
            booking.save()
            self.send_booking_emails(booking)

        messages.success(self.request, _("Your booking was submitted successfully."))
        self.request.session["latest_booking_id"] = booking.pk
        return HttpResponseRedirect(reverse("booking_success"))

    def send_booking_emails(self, booking):
        site_settings = get_site_settings()
        services_text = ", ".join(booking.items.values_list("service_name", flat=True))
        admin_email = site_settings.contact_email or site_settings.smtp_username or "admin@lknailslashes.de"
        email_context = {
            "customer_name": booking.customer_name,
            "booking_reference": booking.reference,
            "services": services_text,
            "total_price": booking.total_price,
            "start_at": timezone.localtime(booking.starts_at),
        }
        admin_subject, admin_body = render_email_template(
            "admin_booking",
            f"New booking {booking.reference}",
            f"{booking.customer_name} booked {services_text} for {timezone.localtime(booking.starts_at)}.",
            email_context,
        )
        send_configured_email(admin_subject, admin_body, [admin_email], site_settings=site_settings)
        customer_subject, customer_body = render_email_template(
            "customer_confirmation",
            f"Booking confirmation {booking.reference}",
            f"Thank you {booking.customer_name}. Your booking for {services_text} starts at {timezone.localtime(booking.starts_at)}.",
            email_context,
        )
        send_configured_email(customer_subject, customer_body, [booking.email], site_settings=site_settings)


class BookingSuccessView(TemplateView):
    template_name = "bookings/booking_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.request.session.get("latest_booking_id")
        booking = (
            Booking.objects.filter(pk=booking_id)
            .prefetch_related("items")
            .first()
        )
        context["booking"] = booking
        return context


def available_slots_view(request):
    appointment_date = parse_date(request.GET.get("date", ""))
    service_ids = request.GET.getlist("services")
    services = list(Service.objects.filter(is_active=True, pk__in=service_ids))
    total_duration, total_price = calculate_totals(services)

    if not appointment_date:
        return JsonResponse(
            {
                "slots": [],
                "total_duration": total_duration,
                "total_price": f"{total_price:.2f}",
                "is_closed": False,
                "message": "",
            }
        )

    working_hour = get_working_hour(appointment_date)
    if not working_hour:
        return JsonResponse(
            {
                "slots": [],
                "total_duration": total_duration,
                "total_price": f"{total_price:.2f}",
                "slot_minutes": get_site_settings().booking_slot_minutes,
                "is_closed": True,
                "message": str(_("The salon is closed on the selected day.")),
            }
        )

    slots = [
        {
            "value": timezone.localtime(slot).strftime("%H:%M"),
            "label": timezone.localtime(slot).strftime("%H:%M"),
        }
        for slot in get_available_start_slots(appointment_date, total_duration)
    ]
    return JsonResponse(
        {
            "slots": slots,
            "total_duration": total_duration,
            "total_price": f"{total_price:.2f}",
            "slot_minutes": get_site_settings().booking_slot_minutes,
            "is_closed": False,
            "message": str(_("No free appointment times are available for the selected services on this date.")) if not slots else "",
            "working_hours": {
                "open": working_hour.open_time.strftime("%H:%M"),
                "close": working_hour.close_time.strftime("%H:%M"),
            },
        }
    )


@staff_member_required
def calendar_view(request):
    requested_start = parse_date(request.GET.get("week_start", ""))
    local_today = timezone.localdate()
    week_start = requested_start or (local_today - timedelta(days=local_today.weekday()))
    week_days = [week_start + timedelta(days=index) for index in range(7)]
    bookings = (
        Booking.objects.exclude(status=Booking.Status.CANCELLED)
        .filter(starts_at__date__gte=week_start, starts_at__date__lte=week_start + timedelta(days=6))
        .order_by("starts_at")
    )
    grouped = {day: [] for day in week_days}
    for booking in bookings:
        grouped[timezone.localtime(booking.starts_at).date()].append(booking)

    return render(
        request,
        "admin/calendar.html",
        {
            "week_days": week_days,
            "calendar_bookings": grouped,
            "previous_week": week_start - timedelta(days=7),
            "next_week": week_start + timedelta(days=7),
        },
    )


@staff_member_required
def dashboard_view(request):
    now = timezone.localtime()
    today = now.date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)

    bookings = Booking.objects.exclude(status=Booking.Status.CANCELLED)
    today_bookings = bookings.filter(starts_at__date=today).select_related()
    top_services = Service.objects.filter(is_active=True).order_by("-booking_count", "name")[:5]
    monthly_revenue = bookings.filter(starts_at__date__gte=this_month_start).aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
    weekly_revenue = bookings.filter(starts_at__date__gte=this_week_start).aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
    today_revenue = today_bookings.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
    capacity = max(get_site_settings().concurrent_capacity, 1)
    active_now = bookings.filter(starts_at__lte=now, ends_at__gte=now).count()

    test_email_form = TestEmailForm()
    if request.method == "POST":
        test_email_form = TestEmailForm(request.POST)
        if test_email_form.is_valid():
            recipient = test_email_form.cleaned_data["recipient"]
            site_settings = get_site_settings()
            sent = send_configured_email(
                "LK Nails & Lashes SMTP test",
                "This is a test email from the LK Nails & Lashes booking system.",
                [recipient],
                site_settings=site_settings,
            )
            if sent:
                messages.success(request, _("Test email sent successfully."))
            else:
                messages.error(request, _("Test email could not be sent. Check SMTP settings in Site Settings."))
            return HttpResponseRedirect(reverse("admin_dashboard"))

    context = {
        "today_bookings": today_bookings,
        "booking_status_counts": {
            "confirmed": bookings.filter(status=Booking.Status.CONFIRMED).count(),
            "pending": bookings.filter(status=Booking.Status.PENDING).count(),
            "cancelled": Booking.objects.filter(status=Booking.Status.CANCELLED).count(),
        },
        "period_totals": {
            "week": bookings.filter(starts_at__date__gte=this_week_start).count(),
            "month": bookings.filter(starts_at__date__gte=this_month_start).count(),
            "year": bookings.filter(starts_at__date__gte=this_year_start).count(),
        },
        "revenue_totals": {
            "today": today_revenue,
            "week": weekly_revenue,
            "month": monthly_revenue,
        },
        "live_capacity": {
            "active_now": active_now,
            "capacity": capacity,
            "utilization_percent": round((active_now / capacity) * 100),
        },
        "top_services": top_services,
        "service_stats": Service.objects.filter(is_active=True).order_by("-booking_count", "name")[:10],
        "test_email_form": test_email_form,
        "smtp_ready": get_site_settings().smtp_is_configured,
    }
    return render(request, "admin/dashboard.html", context)
