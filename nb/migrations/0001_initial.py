# Generated by Django 3.2.16 on 2022-11-19 13:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='诗人名称', max_length=20)),
                ('dynasty', models.CharField(default=None, help_text='诗人所属朝代', max_length=20)),
                ('introduce', models.TextField(default=None, help_text='诗人简介')),
                ('is_delete', models.BooleanField(default=False, help_text='是否删除')),
                ('update_date', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存时间')),
            ],
            options={
                'db_table': 'author',
            },
        ),
        migrations.CreateModel(
            name='Poetry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(default=None, help_text='诗词类型', max_length=20)),
                ('phrase', models.CharField(default=None, help_text='名句', max_length=200)),
                ('explain', models.TextField(default=None, help_text='名句解释')),
                ('appreciation', models.TextField(default=None, help_text='名句赏析')),
                ('name', models.CharField(help_text='诗词名称', max_length=20)),
                ('original', models.TextField(default=None, help_text='诗词原文')),
                ('translation', models.TextField(default=None, help_text='诗词译文')),
                ('background', models.TextField(default=None, help_text='创作背景')),
                ('url', models.CharField(default=None, help_text='诗词地址', max_length=200)),
                ('is_delete', models.BooleanField(default=False, help_text='是否删除')),
                ('update_date', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存时间')),
                ('author', models.ForeignKey(default=None, help_text='诗人ID', on_delete=django.db.models.deletion.CASCADE, to='nb.author')),
            ],
            options={
                'db_table': 'poetry',
            },
        ),
    ]
