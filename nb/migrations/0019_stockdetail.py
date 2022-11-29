# Generated by Django 3.2.16 on 2022-11-28 21:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0018_shareshold_last_day'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default=None, help_text='股票名称', max_length=20)),
                ('code', models.CharField(default=None, help_text='股票代码', max_length=20)),
                ('increPer', models.FloatField(default=0.0, help_text='涨跌百分比')),
                ('increase', models.FloatField(default=0.0, help_text='涨跌额')),
                ('todayStartPri', models.FloatField(default=0.0, help_text='今日开盘价')),
                ('yestodEndPri', models.FloatField(default=0.0, help_text='昨日收盘价')),
                ('nowPri', models.FloatField(default=0.0, help_text='当前价格')),
                ('todayMax', models.FloatField(default=0.0, help_text='今日最高价')),
                ('todayMin', models.FloatField(default=0.0, help_text='今日最低价')),
                ('competitivePri', models.FloatField(default=0.0, help_text='竞买价')),
                ('reservePri', models.FloatField(default=0.0, help_text='竞卖价')),
                ('traNumber', models.IntegerField(default=0, help_text='成交量')),
                ('traAmount', models.FloatField(default=0.0, help_text='成交金额')),
                ('buyOne', models.FloatField(default=0.0, help_text='买一')),
                ('buyOnePri', models.FloatField(default=0.0, help_text='买一报价')),
                ('buyTwo', models.FloatField(default=0.0, help_text='买二')),
                ('buyTwoPri', models.FloatField(default=0.0, help_text='买二报价')),
                ('buyThree', models.FloatField(default=0.0, help_text='买三')),
                ('buyThreePri', models.FloatField(default=0.0, help_text='买三报价')),
                ('buyFour', models.FloatField(default=0.0, help_text='买四')),
                ('buyFourPri', models.FloatField(default=0.0, help_text='买四报价')),
                ('buyFive', models.FloatField(default=0.0, help_text='买五')),
                ('buyFivePri', models.FloatField(default=0.0, help_text='买五报价')),
                ('sellOne', models.FloatField(default=0.0, help_text='卖一')),
                ('sellOnePri', models.FloatField(default=0.0, help_text='卖一报价')),
                ('sellTwo', models.FloatField(default=0.0, help_text='卖二')),
                ('sellTwoPri', models.FloatField(default=0.0, help_text='卖二报价')),
                ('sellThree', models.FloatField(default=0.0, help_text='卖三')),
                ('sellThreePri', models.FloatField(default=0.0, help_text='卖三报价')),
                ('sellFour', models.FloatField(default=0.0, help_text='卖四')),
                ('sellFourPri', models.FloatField(default=0.0, help_text='卖四报价')),
                ('sellFive', models.FloatField(default=0.0, help_text='卖五')),
                ('sellFivePri', models.FloatField(default=0.0, help_text='卖五报价')),
                ('date', models.FloatField(default=0.0, help_text='日期')),
                ('time', models.FloatField(default=0.0, help_text='时间')),
                ('dot', models.FloatField(default=0.0, help_text='当前价格')),
                ('nowPic', models.FloatField(default=0.0, help_text='涨量')),
                ('rate', models.FloatField(default=0.0, help_text='涨幅(%)')),
                ('nowTraAmount', models.IntegerField(default=0, help_text='成交额(万)')),
                ('nowTraNumber', models.IntegerField(default=0, help_text='成交量')),
                ('minurl', models.CharField(default=None, help_text='分时K线图', max_length=200)),
                ('dayurl', models.CharField(default=None, help_text='日K线图', max_length=200)),
                ('weekurl', models.CharField(default=None, help_text='周K线图', max_length=200)),
                ('monthurl', models.CharField(default=None, help_text='月K线图', max_length=200)),
            ],
            options={
                'db_table': 'StockDetail',
            },
        ),
    ]
