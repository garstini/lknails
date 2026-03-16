from django.contrib import admin

from bookings.models import Booking, BookingItem


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0
    readonly_fields = ("service", "service_name", "category", "subcategory", "duration_minutes", "price")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer_name", "starts_at", "ends_at", "total_duration_minutes", "total_price", "status")
    list_filter = ("status", "starts_at")
    search_fields = ("reference", "customer_name", "email", "phone")
    inlines = [BookingItemInline]
