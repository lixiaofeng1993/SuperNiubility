# Generated by Django 3.2.16 on 2022-12-07 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0029_message_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareshold',
            name='color',
            field=models.CharField(default='red', help_text='折线颜色', max_length=20, null=True),
        ),
    ]