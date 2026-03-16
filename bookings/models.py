from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from services.models import Service


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELLED = "cancelled", _("Cancelled")

    reference = models.CharField(max_length=20, unique=True, blank=True)
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(blank=True, null=True)
    total_duration_minutes = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starts_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = timezone.localtime().strftime("LK%y%m%d%H%M%S")
        if self.total_duration_minutes and self.starts_at:
            self.ends_at = self.starts_at + timedelta(minutes=self.total_duration_minutes)
        return super().save(*args, **kwargs)

    def recalculate(self):
        items = list(self.items.select_related("service"))
        self.total_duration_minutes = sum(item.duration_minutes for item in items)
        self.total_price = sum((item.price for item in items), Decimal("0.00"))
        if self.starts_at:
            self.ends_at = self.starts_at + timedelta(minutes=self.total_duration_minutes)

    def __str__(self):
        return f"{self.reference} - {self.customer_name}"


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, related_name="items", on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name="booking_items", on_delete=models.PROTECT)
    category = models.CharField(max_length=120)
    subcategory = models.CharField(max_length=120, blank=True, default="-")
    service_name = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.service_name
