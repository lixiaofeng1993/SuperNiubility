# Generated by Django 3.2.16 on 2022-12-29 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0049_auto_20221220_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareshold',
            name='buy_price',
            field=models.FloatField(default=0.0, help_text='买入价'),
        ),
    ]
