# Generated by Django 3.2.16 on 2023-01-03 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0056_stockkdj_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockkdj',
            name='t',
        ),
        migrations.AlterField(
            model_name='stockkdj',
            name='time',
            field=models.DateTimeField(help_text='时间', null=True, verbose_name='时间'),
        ),
    ]
