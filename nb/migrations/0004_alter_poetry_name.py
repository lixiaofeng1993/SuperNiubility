# Generated by Django 3.2.16 on 2022-11-19 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0003_alter_poetry_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poetry',
            name='name',
            field=models.CharField(help_text='诗词名称', max_length=200),
        ),
    ]
