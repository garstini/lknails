from django.contrib import admin

from services.models import Promotion, Service, ServiceImage


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


class PromotionInline(admin.TabularInline):
    model = Promotion
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "subcategory", "price", "duration_minutes", "featured", "is_active")
    list_filter = ("category", "is_active", "featured")
    search_fields = ("name", "category", "subcategory")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceImageInline, PromotionInline]


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "service", "start_at", "end_at", "is_active")
    list_filter = ("is_active",)
