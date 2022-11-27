# Generated by Django 3.2.16 on 2022-11-27 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nb', '0016_auto_20221125_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareshold',
            name='is_profit',
            field=models.BooleanField(default=False, help_text='盈转亏、亏转盈'),
        ),
        migrations.AddField(
            model_name='shareshold',
            name='user',
            field=models.ForeignKey(default='', help_text='用户id', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
