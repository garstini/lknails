from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=120)
    subcategory = models.CharField(max_length=120, blank=True, default="-")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    booking_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "subcategory", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Service.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        return super().save(*args, **kwargs)

    @property
    def active_promotion(self):
        now = timezone.now()
        return self.promotions.filter(is_active=True, start_at__lte=now, end_at__gte=now).order_by("promotional_price").first()

    @property
    def current_price(self):
        promotion = self.active_promotion
        return promotion.final_price if promotion else self.price

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def gallery_tone(self):
        tones = {
            "Wimpern": "tone-lashes",
            "Nägel": "tone-nails",
        }
        return tones.get(self.category, "tone-neutral")

    def __str__(self):
        return self.name


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="services/", blank=True)
    alt_text = models.CharField(max_length=160, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service.name} image"


class Promotion(models.Model):
    service = models.ForeignKey(Service, related_name="promotions", on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    promotional_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_at"]

    @property
    def final_price(self):
        if self.promotional_price is not None:
            return self.promotional_price
        if self.discount_percent is not None:
            discount = Decimal("1.00") - (self.discount_percent / Decimal("100"))
            return (self.service.price * discount).quantize(Decimal("0.01"))
        return self.service.price

    def __str__(self):
        return self.title
