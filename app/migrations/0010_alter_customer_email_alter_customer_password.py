# Generated by Django 5.0.3 on 2024-04-22 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_customer_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
