# Generated by Django 3.2.16 on 2022-12-15 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0040_auto_20221214_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='inflowstock',
            name='date',
            field=models.DateTimeField(help_text='日期', null=True, verbose_name='日期'),
        ),
    ]