# Generated by Django 5.0.3 on 2024-04-22 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_customer_email_alter_customer_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=255, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='username',
            field=models.CharField(max_length=200, verbose_name='Tên người dùng'),
        ),
    ]
