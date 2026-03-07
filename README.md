# Shots By Beysos — Django Order Form

## Quick Start

```bash
# 1. Clone / extract the project
cd shotsbybeysos

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in your Stripe keys and email credentials

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (for the admin panel)
python manage.py createsuperuser

# 7. Start the dev server
python manage.py runserver
```

Open http://127.0.0.1:8000 to see the order form.
Open http://127.0.0.1:8000/admin to manage orders.

---

## Project Structure

```
shotsbybeysos/
├── manage.py
├── requirements.txt
├── .env.example
├── shotsbybeysos/          # Django project config
│   ├── settings.py         ← Stripe keys, email, price config here
│   ├── urls.py
│   └── wsgi.py
└── orders/                 # The order form app
    ├── models.py           ← Order + OrderPhoto database models
    ├── views.py            ← Order form, PaymentIntent, save order, webhook
    ├── urls.py             ← URL routes
    ├── admin.py            ← Admin panel config
    ├── migrations/
    └── templates/orders/
        └── order_form.html ← The full styled order form template
```

---

## Configuration (settings.py / .env)

| Variable                | Description                                      |
|-------------------------|--------------------------------------------------|
| `STRIPE_PUBLISHABLE_KEY`| Stripe pk_test_ or pk_live_ key                  |
| `STRIPE_SECRET_KEY`     | Stripe sk_test_ or sk_live_ key                  |
| `STRIPE_WEBHOOK_SECRET` | From Stripe dashboard webhook settings           |
| `PRICE_PER_PHOTO`       | Price in cents (default: 2500 = $25.00)          |
| `EMAIL_HOST_USER`       | SMTP email address                               |
| `EMAIL_HOST_PASSWORD`   | SMTP password / app password                     |
| `STUDIO_EMAIL`          | Email that receives new order notifications      |

---

## Stripe Webhook Setup

1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://yourdomain.com/webhook/stripe/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy the signing secret into `STRIPE_WEBHOOK_SECRET` in your `.env`

---

## Email in Production

In `settings.py`, change:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```
Then fill in your SMTP credentials in `.env`.
For Gmail, use an App Password (not your main password).
