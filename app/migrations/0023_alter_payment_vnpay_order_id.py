# Generated by Django 5.0.3 on 2024-05-01 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_alter_payment_vnpay_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment_vnpay',
            name='order_id',
            field=models.IntegerField(blank=True, default=0, max_length=255, null=True),
        ),
    ]
