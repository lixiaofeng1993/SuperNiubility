# Generated by Django 3.2.16 on 2022-11-19 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0005_shares'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shares',
            name='date_time',
            field=models.CharField(help_text='股票日期', max_length=20),
        ),
    ]
