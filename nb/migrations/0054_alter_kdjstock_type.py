# Generated by Django 3.2.16 on 2023-01-03 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0053_remove_stockdeal_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kdjstock',
            name='type',
            field=models.CharField(help_text='金叉-死叉', max_length=20),
        ),
    ]
