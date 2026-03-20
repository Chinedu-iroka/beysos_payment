import json
import stripe
import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Order, OrderPhoto, GalleryImage, OrderCartItem

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    return render(request, 'orders/home.html')


def gallery(request):
    from .models import GalleryCategory
    categories = GalleryCategory.objects.prefetch_related('images').all()

    # Attach cover image to each category in Python (not in template)
    for cat in categories:
        cover = cat.images.filter(is_cover=True, is_visible=True).first()
        if not cover:
            # Fallback to first visible image if no cover is set
            cover = cat.images.filter(is_visible=True).first()
        cat.cover_image = cover

    return render(request, 'orders/gallery.html', {'categories': categories})

def gallery_category(request, slug):
    from .models import GalleryCategory
    from django.shortcuts import get_object_or_404
    category   = get_object_or_404(GalleryCategory, slug=slug)
    categories = GalleryCategory.objects.all()
    images     = category.images.filter(is_visible=True)
    return render(request, 'orders/gallery_category.html', {
        'category':   category,
        'categories': categories,
        'images':     images,
    })

@require_POST
def contact_submit(request):
    name    = request.POST.get('name', '').strip()
    email   = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    if not name or not email or not message:
        return JsonResponse({'ok': False, 'error': 'Please fill in all fields.'}, status=400)
    try:
        send_mail(
            subject=f'New Contact Message from {name}',
            message=f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.STUDIO_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f'Contact form email failed: {e}')
        return JsonResponse({'ok': False, 'error': 'Could not send message. Please try again.'}, status=500)


def order_form(request):
    cart_amount = request.GET.get('amount')
    try:
        price_per_photo = int(cart_amount) if cart_amount else settings.PRICE_PER_PHOTO
    except ValueError:
        price_per_photo = settings.PRICE_PER_PHOTO

    return render(request, 'orders/order_form.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'price_per_photo':        price_per_photo,
        'currency':               settings.CURRENCY,
        'prefill_style':          request.GET.get('style', ''),
        'prefill_notes':          request.GET.get('notes', ''),
        'prefill_count':          request.GET.get('count', '1'),
        'cart_amount':            price_per_photo,
    })


@require_POST
def create_payment_intent(request):
    try:
        data        = json.loads(request.body)
        photo_count = int(data.get('photo_count', 1))

        # Use explicit amount from cart if provided, otherwise calculate from photo count
        explicit_amount = data.get('amount')
        if explicit_amount:
            amount = int(explicit_amount)
        else:
            amount = settings.PRICE_PER_PHOTO * photo_count

        intent = stripe.PaymentIntent.create(
            amount   = amount,
            currency = settings.CURRENCY,
            metadata = {
                'client_name':   data.get('client_name', ''),
                'client_email':  data.get('client_email', ''),
                'booking_id':    data.get('booking_id', ''),
                'style_chosen':  data.get('style_chosen', ''),
                'photo_count':   photo_count,
                'special_notes': data.get('special_notes', ''),
            },
            automatic_payment_methods={'enabled': True},
        )
        return JsonResponse({'clientSecret': intent.client_secret})
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Server error. Please try again.'}, status=500)


@require_POST
def save_order(request):
    try:
        name        = request.POST.get('client_name', '').strip()
        email       = request.POST.get('client_email', '').strip()
        booking_id  = request.POST.get('booking_id', '').strip()
        style       = request.POST.get('style_chosen', '').strip()
        notes       = request.POST.get('special_notes', '').strip()
        payment_id  = request.POST.get('stripe_payment_id', '').strip()
        photo_count    = len(request.FILES.getlist('photos'))
        cart_json      = request.POST.get('cart_items', '[]')
        cart_items_list = json.loads(cart_json) if cart_json else []
        cart_count     = len(cart_items_list)
        stripe_amount = request.POST.get('amount_paid')
        if stripe_amount:
            amount = int(stripe_amount) / 100
        else:
            amount = (settings.PRICE_PER_PHOTO * max(photo_count, 1)) / 100
        order = Order.objects.create(
            booking_id=booking_id, client_name=name, client_email=email,
            style_chosen=style, special_notes=notes, photo_count=cart_count if cart_count > 0 else photo_count,
            amount_paid=amount, currency=settings.CURRENCY,
            stripe_payment_id=payment_id, status='paid',
        )
        for photo_file in request.FILES.getlist('photos'):
            OrderPhoto.objects.create(order=order, photo=photo_file, filename=photo_file.name)

        for item in cart_items_list:
            gallery_image = None
            try:
                gallery_image = GalleryImage.objects.get(id=item.get('id'))
            except GalleryImage.DoesNotExist:
                pass
            OrderCartItem.objects.create(
                order         = order,
                gallery_image = gallery_image,
                title         = item.get('title', ''),
                category      = item.get('category', ''),
                price         = item.get('price', 0),
                image_url     = item.get('src', ''),
            )

        threading.Thread(target=_send_client_confirmation, args=(order,), daemon=True).start()
        threading.Thread(target=_send_studio_notification, args=(order,), daemon=True).start()
        return JsonResponse({'orderId': order.short_id})
    except Exception as e:
        logger.error(f"Error saving order: {e}")
        return JsonResponse({'error': 'Could not save order. Please contact support.'}, status=500)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload    = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    if event['type'] == 'payment_intent.succeeded':
        _handle_payment_succeeded(event['data']['object'])
    return HttpResponse(status=200)


def _handle_payment_succeeded(intent):
    try:
        order = Order.objects.get(stripe_payment_id=intent['id'])
        if order.status == 'pending':
            order.status = 'paid'
            order.save()
    except Order.DoesNotExist:
        pass


def _send_client_confirmation(order):
    try:
        send_mail(
            subject=f"Order Confirmed — Shots By Beysos (#{order.short_id})",
            message=f"Hi {order.client_name},\n\nThank you for your order!\n\nOrder ID: {order.short_id}\nStyle: {order.style_chosen}\nPhotos: {order.photo_count}\nAmount: ${order.amount_paid:.2f}\n\nYour transformed photo will be delivered within 24–48 hours.\n\nWarm regards,\nShots By Beysos",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.client_email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Client email failed: {e}")


def _send_studio_notification(order):
    try:
        send_mail(
            subject=f"New Order #{order.short_id} — {order.style_chosen}",
            message=f"New order!\n\nClient: {order.client_name}\nEmail: {order.client_email}\nBooking ID: {order.booking_id}\nStyle: {order.style_chosen}\nPhotos: {order.photo_count}\nAmount: ${order.amount_paid:.2f}\nStripe ID: {order.stripe_payment_id}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.STUDIO_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Studio email failed: {e}")