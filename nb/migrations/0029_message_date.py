# Generated by Django 3.2.16 on 2022-12-01 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0028_remove_message_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='date',
            field=models.DateTimeField(help_text='写入时间', null=True, verbose_name='写入时间'),
        ),
    ]
