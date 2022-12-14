# Generated by Django 3.2.16 on 2023-01-04 19:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0058_stockmacd'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockRSI',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rsi1', models.FloatField(default=0.0, help_text='rsi-6天值')),
                ('rsi2', models.FloatField(default=0.0, help_text='rsi-12天值')),
                ('rsi3', models.FloatField(default=0.0, help_text='rsi-24天值')),
                ('time', models.DateTimeField(help_text='时间', null=True, verbose_name='时间')),
                ('name', models.CharField(help_text='股票名称', max_length=20)),
                ('type', models.CharField(help_text='超买-超卖', max_length=20)),
                ('is_delete', models.BooleanField(default=False, help_text='是否删除')),
                ('update_date', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存时间')),
                ('shares_hold', models.ForeignKey(default='', help_text='持仓股票ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='nb.shareshold')),
            ],
            options={
                'db_table': 'stock_rsi',
            },
        ),
    ]
