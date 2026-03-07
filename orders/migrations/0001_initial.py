from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id',                models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('booking_id',        models.CharField(max_length=50)),
                ('client_name',       models.CharField(max_length=255)),
                ('client_email',      models.EmailField()),
                ('style_chosen',      models.CharField(max_length=100)),
                ('special_notes',     models.TextField(blank=True)),
                ('photo_count',       models.PositiveIntegerField(default=1)),
                ('amount_paid',       models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('currency',          models.CharField(default='usd', max_length=10)),
                ('stripe_payment_id', models.CharField(blank=True, max_length=255)),
                ('status',            models.CharField(choices=[('pending','Pending Payment'),('paid','Paid'),('processing','Processing'),('delivered','Delivered'),('refunded','Refunded')], default='pending', max_length=20)),
                ('created_at',        models.DateTimeField(auto_now_add=True)),
                ('updated_at',        models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderPhoto',
            fields=[
                ('id',       models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo',    models.ImageField(upload_to='uploads/%Y/%m/%d/')),
                ('filename', models.CharField(max_length=255)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('order',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='orders.order')),
            ],
        ),
    ]
