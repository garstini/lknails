from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .models import Appointment, Customer, Service, Staff, Review


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class AppointmentForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Wählen Sie einen oder mehrere Services"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select your preferred date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Select your preferred time"
    )

    class Meta:
        model = Appointment
        fields = ['services', 'date', 'time', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['services'].queryset = Service.objects.filter(is_active=True)
        # Group services by category for better UI
        services_by_category = {}
        for service in Service.objects.filter(is_active=True).select_related('category'):
            if service.category.name not in services_by_category:
                services_by_category[service.category.name] = []
            services_by_category[service.category.name].append(service)

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today():
            raise ValidationError("Cannot book appointments in the past.")
        
        # Don't allow bookings more than 3 months in advance
        max_date = date.today() + timedelta(days=90)
        if selected_date > max_date:
            raise ValidationError("Cannot book appointments more than 3 months in advance.")
        
        return selected_date

    def clean_time(self):
        selected_time = self.cleaned_data['time']
        
        # Business hours: 9 AM to 6 PM
        if selected_time.hour < 9 or selected_time.hour >= 18:
            raise ValidationError("Please select a time between 9:00 AM and 6:00 PM.")
        
        # Only allow 15-minute intervals
        if selected_time.minute not in [0, 15, 30, 45]:
            raise ValidationError("Please select times in 15-minute intervals (e.g., 10:00, 10:15, 10:30, 10:45).")
        
        return selected_time

    def clean(self):
        cleaned_data = super().clean()
        selected_date = cleaned_data.get('date')
        selected_time = cleaned_data.get('time')
        selected_services = cleaned_data.get('services')

        if selected_date and selected_time and selected_services:
            # Check if services are selected
            if not selected_services:
                raise ValidationError("Bitte wählen Sie mindestens einen Service.")
            
            # Calculate total duration for all selected services
            total_duration = sum(service.duration_minutes for service in selected_services)
            
            # Check if we can accommodate this appointment with 3 staff limit
            appointments_at_time = Appointment.objects.filter(
                date=selected_date,
                time=selected_time,
                status__in=['confirmed', 'pending']
            ).count()
            
            if appointments_at_time >= 3:
                raise ValidationError(
                    "Entschuldigung, alle unsere Mitarbeiterinnen sind zu dieser Zeit gebucht. Bitte wählen Sie einen anderen Zeitslot."
                )
            
            # Check if there's enough time before the next appointment
            appointment_datetime = datetime.combine(selected_date, selected_time)
            end_time = appointment_datetime + timedelta(minutes=total_duration)
            
            # Find conflicts with existing appointments
            existing_appointments = Appointment.objects.filter(
                date=selected_date,
                status__in=['confirmed', 'pending']
            )
            
            for appointment in existing_appointments:
                existing_start = datetime.combine(appointment.date, appointment.time)
                existing_end = existing_start + timedelta(minutes=appointment.total_duration)
                
                # Check for time conflicts
                if (appointment_datetime < existing_end and end_time > existing_start):
                    # Count how many appointments are already scheduled during this conflict
                    overlapping_count = 0
                    for apt in existing_appointments:
                        apt_start = datetime.combine(apt.date, apt.time)
                        apt_end = apt_start + timedelta(minutes=apt.total_duration)
                        if (appointment_datetime < apt_end and end_time > apt_start):
                            overlapping_count += 1
                    
                    if overlapping_count >= 3:
                        raise ValidationError(
                            f"Dieser Zeitslot kollidiert mit bestehenden Terminen und alle Mitarbeiterinnen wären beschäftigt. "
                            f"Bitte wählen Sie eine andere Zeit."
                        )

        return cleaned_data


class ServiceFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=None,
        empty_label="All Categories",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price_min = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'})
    )
    price_max = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ServiceCategory
        self.fields['category'].queryset = ServiceCategory.objects.all()


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = Customer
        fields = ['phone', 'birth_date', 'address', 'notes']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, user, commit=True):
        customer = super().save(commit=False)
        customer.user = user
        
        # Update user fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            customer.save()
        return customer


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES, attrs={
                'class': 'rating-radio'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Teilen Sie Ihre Erfahrung mit anderen Kunden...',
                'maxlength': 1000
            }),
        }
        labels = {
            'rating': 'Wie würden Sie Ihre Erfahrung bewerten?',
            'comment': 'Ihr Kommentar (optional)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = True
        self.fields['comment'].required = False