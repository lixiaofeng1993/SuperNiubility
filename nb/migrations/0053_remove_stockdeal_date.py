# Generated by Django 3.2.16 on 2023-01-02 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0052_stockdeal_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockdeal',
            name='date',
        ),
    ]
