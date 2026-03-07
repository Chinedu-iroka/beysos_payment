from django.db import models
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending Payment'),
        ('paid',       'Paid'),
        ('processing', 'Processing'),
        ('delivered',  'Delivered'),
        ('refunded',   'Refunded'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_id      = models.CharField(max_length=50)
    client_name     = models.CharField(max_length=255)
    client_email    = models.EmailField()
    style_chosen    = models.CharField(max_length=100)
    special_notes   = models.TextField(blank=True)
    photo_count     = models.PositiveIntegerField(default=1)
    amount_paid     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency        = models.CharField(max_length=10, default='usd')
    stripe_payment_id = models.CharField(max_length=255, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {str(self.id)[-8:].upper()} — {self.client_name} ({self.style_chosen})"

    @property
    def short_id(self):
        return str(self.id)[-8:].upper()


class OrderPhoto(models.Model):
    order    = models.ForeignKey(Order, related_name='photos', on_delete=models.CASCADE)
    photo    = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} (Order {self.order.short_id})"

class GalleryCategory(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0, help_text="Controls display order. Lower numbers appear first.")

    class Meta:
        ordering = ['order', 'name']
        verbose_name        = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category   = models.ForeignKey(GalleryCategory, related_name='images', on_delete=models.CASCADE)
    image      = models.ImageField(upload_to='gallery/%Y/%m/')
    title      = models.CharField(max_length=200, blank=True)
    is_cover   = models.BooleanField(default=False, help_text="Use this image as the category cover photo.")
    is_visible = models.BooleanField(default=True, help_text="Uncheck to hide this image from the gallery.")
    uploaded   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_cover', '-uploaded']

    def __str__(self):
        return f"{self.title or 'Image'} — {self.category.name}"