# Generated by Django 5.0.3 on 2024-04-22 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_remove_customer_email_remove_customer_username_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='user',
        ),
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(default='', max_length=255, unique=True, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='customer',
            name='username',
            field=models.CharField(default='', max_length=200, verbose_name='Tên người dùng'),
        ),
    ]