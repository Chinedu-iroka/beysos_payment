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
    fields          = ('title', 'category', 'price', 'image_url')
    readonly_fields = ('title', 'category', 'price', 'image_url')

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
    search_fields = ('filename', 'order__client_name')


class GalleryImageInline(admin.TabularInline):
    model  = GalleryImage
    extra  = 3
    fields = ('image', 'title', 'price', 'is_cover', 'is_visible')


# class OrderCartItemInline(admin.TabularInline):
#     model  = OrderCartItem
#     extra  = 0
#     fields = ('title', 'category', 'price', 'image_url')
#     readonly_fields = ('title', 'category', 'price', 'image_url')


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'order', 'image_count')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    inlines       = [GalleryImageInline]

    def image_count(self, obj):
        return obj.images.filter(is_visible=True).count()
    image_count.short_description = 'Images'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'price', 'is_cover', 'is_visible', 'uploaded')
    list_editable = ('price', 'is_cover', 'is_visible')
    list_filter   = ('category', 'is_visible')
    search_fields = ('title',)