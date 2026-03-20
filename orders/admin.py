import json
from django.contrib import admin
from .models import Order, OrderPhoto, GalleryCategory, GalleryImage, OrderCartItem


class OrderPhotoInline(admin.TabularInline):
    model        = OrderPhoto
    extra        = 0
    verbose_name         = 'Uploaded Image'
    verbose_name_plural  = 'Uploaded Images'
    readonly_fields = ('filename', 'photo', 'uploaded')


class OrderCartItemInline(admin.TabularInline):
    model           = OrderCartItem
    extra           = 0
    fields          = ('image_preview', 'title', 'category', 'price')
    readonly_fields = ('image_preview', 'title', 'category', 'price')

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image_url:
            return format_html('<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:4px;"/>', obj.image_url)
        elif obj.gallery_image and obj.gallery_image.image:
            return format_html('<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:4px;"/>', obj.gallery_image.image.url)
        return '—'
    image_preview.short_description = 'Image'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('short_id', 'client_name', 'client_email', 'style_chosen', 'photo_count', 'amount_paid', 'status', 'created_at')
    list_filter     = ('status', 'style_chosen', 'created_at')
    search_fields   = ('client_name', 'client_email', 'booking_id', 'stripe_payment_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'stripe_payment_id')
    inlines         = [OrderPhotoInline, OrderCartItemInline]

    fieldsets = (
        ('Client Info',      {'fields': ('client_name', 'client_email', 'booking_id')}),
        ('Order Details',    {'fields': ('style_chosen', 'special_notes', 'photo_count', 'amount_paid', 'currency')}),
        ('Payment & Status', {'fields': ('stripe_payment_id', 'status')}),
        ('Timestamps',       {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(OrderPhoto)
class OrderPhotoAdmin(admin.ModelAdmin):
    list_display  = ('filename', 'order', 'uploaded')
    fields = ('image', 'title', 'price', 'is_cover', 'is_visible')


# class OrderCartItemInline(admin.TabularInline):
#     model  = OrderCartItem
#     extra  = 0
#     fields = ('title', 'category', 'price', 'image_url')
#     readonly_fields = ('title', 'category', 'price', 'image_url')


class GalleryImageInline(admin.TabularInline):
    model  = GalleryImage
    extra  = 3
    fields = ('image', 'title', 'price', 'is_cover', 'is_visible')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'price', 'is_cover', 'is_visible', 'uploaded')
    list_editable = ('price', 'is_cover', 'is_visible')
    list_filter   = ('category', 'is_visible')
    search_fields = ('title',)