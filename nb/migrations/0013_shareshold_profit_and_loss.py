# Generated by Django 3.2.16 on 2022-11-24 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0012_auto_20221123_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareshold',
            name='profit_and_loss',
            field=models.FloatField(default=0.0, help_text='持仓盈亏', null=True),
        ),
    ]
