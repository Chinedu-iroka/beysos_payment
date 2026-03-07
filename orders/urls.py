from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.home,                  name='home'),
    path('gallery/',            views.gallery,               name='gallery'),
    path('gallery/<slug:slug>/',       views.gallery_category,      name='gallery_category'),
    path('order/',              views.order_form,            name='order_form'),
    path('api/payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/save-order/',     views.save_order,            name='save_order'),
    path('api/contact/',        views.contact_submit,        name='contact_submit'),
    path('webhook/stripe/',     views.stripe_webhook,        name='stripe_webhook'),
]