from django.contrib import admin

from bookings.models import Booking, BookingItem


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0
    fields = ("service", "service_name", "category", "subcategory", "duration_minutes", "price")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer_name", "phone", "starts_at", "ends_at", "total_duration_minutes", "total_price", "status")
    list_filter = ("status", "starts_at")
    search_fields = ("reference", "customer_name", "email", "phone")
    date_hierarchy = "starts_at"
    actions = ("mark_confirmed", "mark_cancelled")
    fieldsets = (
        ("Customer", {"fields": ("customer_name", "phone", "email", "note")}),
        ("Appointment", {"fields": ("status", "starts_at", "ends_at")}),
        ("Totals", {"fields": ("total_duration_minutes", "total_price")}),
        ("System", {"fields": ("reference", "created_at")}),
    )
    readonly_fields = ("reference", "created_at")
    inlines = [BookingItemInline]

    @admin.action(description="Mark selected bookings as confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Booking.Status.CONFIRMED)

    @admin.action(description="Mark selected bookings as cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Booking.Status.CANCELLED)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if instance.service_id:
                instance.service_name = instance.service.name
                instance.category = instance.service.category
                instance.subcategory = instance.service.subcategory
                instance.duration_minutes = instance.service.duration_minutes
                instance.price = instance.service.current_price
            instance.save()
        formset.save_m2m()
        booking = form.instance
        booking.recalculate()
        booking.save()
