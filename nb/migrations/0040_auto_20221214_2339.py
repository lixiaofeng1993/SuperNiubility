# Generated by Django 3.2.16 on 2022-12-14 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0039_stockdetail_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shareshold',
            name='down_price',
        ),
        migrations.RemoveField(
            model_name='shareshold',
            name='top_price',
        ),
    ]
