# Generated by Django 3.2.16 on 2023-01-02 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0051_stockdeal'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockdeal',
            name='date',
            field=models.DateTimeField(help_text='完整时间', null=True, verbose_name='完整时间'),
        ),
    ]
