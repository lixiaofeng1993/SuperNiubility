# Generated by Django 3.2.16 on 2022-12-15 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0042_auto_20221215_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='type',
            field=models.CharField(help_text='跳转页面', max_length=20, null=True),
        ),
    ]
