# Generated by Django 3.2.16 on 2023-01-03 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0054_alter_kdjstock_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='KDJStock',
            new_name='StockKDJ',
        ),
    ]