# Generated by Django 5.0.3 on 2024-04-22 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_customer_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(default='', max_length=255, verbose_name='Email'),
        ),
    ]
