# Generated by Django 3.2.16 on 2022-11-19 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poetry',
            name='author',
            field=models.ForeignKey(default='', help_text='诗人ID', on_delete=django.db.models.deletion.CASCADE, to='nb.author'),
        ),
    ]
