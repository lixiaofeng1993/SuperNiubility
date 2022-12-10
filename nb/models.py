import uuid

from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth.models import User


class Author(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, help_text="诗人名称")
    dynasty = models.CharField(max_length=20, default=None, help_text="诗人所属朝代")
    introduce = models.TextField(default=None, help_text="诗人简介")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    class Meta:
        db_table = "author"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class Poetry(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, default=None, help_text="诗词类型")
    phrase = models.CharField(max_length=200, default=None, help_text="名句")
    explain = models.TextField(default=None, help_text="名句解释")
    appreciation = models.TextField(default=None, help_text="名句赏析")
    name = models.CharField(max_length=200, null=False, help_text="诗词名称")
    original = models.TextField(default=None, help_text="诗词原文")
    translation = models.TextField(default=None, help_text="诗词译文")
    background = models.TextField(default=None, help_text="创作背景")
    url = models.CharField(max_length=200, default=None, help_text="诗词地址")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default="", null=True, help_text="诗人ID")

    class Meta:
        db_table = "poetry"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class SharesHold(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, help_text="持仓股票名称")
    code = models.CharField(max_length=20, null=False, help_text="持仓股票代码")
    number = models.IntegerField(default=0, null=False, help_text="持仓数量")
    days = models.IntegerField(default=0, null=False, help_text="持仓天数")
    cost_price = models.FloatField(default=0.00, null=False, help_text="成本价")
    profit_and_loss = models.FloatField(default=0.00, null=True, help_text="持仓盈亏")
    last_close_price = models.FloatField(default=0.00, null=True, help_text="上一天收盘价")
    last_day = models.DateTimeField("上一天日期", null=True, help_text="上一天日期")
    today_price = models.FloatField(default=0.00, null=True, help_text="当天盈亏")
    color = models.CharField(max_length=20, default="red", null=True, help_text="折线颜色")
    is_profit = models.BooleanField(default=False, help_text="盈转亏、亏转盈")
    is_detail = models.BooleanField(default=False, help_text="是否查看详情")  # 唯一标识，只能设置一个
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="", null=True, help_text="用户id")

    class Meta:
        db_table = "shares_hold"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class Shares(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    date_time = models.CharField(max_length=20, null=False, help_text="股票日期")
    open_price = models.FloatField(default=0.00, help_text="开盘价格")
    new_price = models.FloatField(default=0.00, help_text="收盘价格")
    top_price = models.FloatField(default=0.00, help_text="最高价格")
    down_price = models.FloatField(default=0.00, help_text="最低价格")
    turnover = models.IntegerField(default=0, help_text="成交量")
    business_volume = models.IntegerField(default=0, help_text="成交额")
    amplitude = models.FloatField(default=0.00, help_text="振幅")
    rise_and_fall = models.FloatField(default=0.00, help_text="涨跌幅")
    rise_and_price = models.FloatField(default=0.00, help_text="涨跌额")
    turnover_rate = models.FloatField(default=0.00, help_text="换手率")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)
    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "shares"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class StockDetail(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    increPer = models.FloatField(default=0.00, help_text="涨跌百分比")
    increase = models.FloatField(default=0.00, help_text="涨跌额")
    todayStartPri = models.FloatField(default=0.00, help_text="今日开盘价")
    yestodEndPri = models.FloatField(default=0.00, help_text="昨日收盘价")
    nowPri = models.FloatField(default=0.00, help_text="当前价格")
    todayMax = models.FloatField(default=0.00, help_text="今日最高价")
    todayMin = models.FloatField(default=0.00, help_text="今日最低价")
    competitivePri = models.FloatField(default=0.00, help_text="竞买价")
    reservePri = models.FloatField(default=0.00, help_text="竞卖价")
    traNumber = models.IntegerField(default=0, help_text="成交量")
    traAmount = models.FloatField(default=0.00, help_text="成交金额")
    buyOne = models.IntegerField(default=0, help_text="买一")
    buyOnePri = models.FloatField(default=0.00, help_text="买一报价")
    buyTwo = models.IntegerField(default=0, help_text="买二")
    buyTwoPri = models.FloatField(default=0.00, help_text="买二报价")
    buyThree = models.IntegerField(default=0, help_text="买三")
    buyThreePri = models.FloatField(default=0.00, help_text="买三报价")
    buyFour = models.IntegerField(default=0, help_text="买四")
    buyFourPri = models.FloatField(default=0.00, help_text="买四报价")
    buyFive = models.IntegerField(default=0, help_text="买五")
    buyFivePri = models.FloatField(default=0.00, help_text="买五报价")
    sellOne = models.IntegerField(default=0, help_text="卖一")
    sellOnePri = models.FloatField(default=0.00, help_text="卖一报价")
    sellTwo = models.IntegerField(default=0, help_text="卖二")
    sellTwoPri = models.FloatField(default=0.00, help_text="卖二报价")
    sellThree = models.IntegerField(default=0, help_text="卖三")
    sellThreePri = models.FloatField(default=0.00, help_text="卖三报价")
    sellFour = models.IntegerField(default=0, help_text="卖四")
    sellFourPri = models.FloatField(default=0.00, help_text="卖四报价")
    sellFive = models.IntegerField(default=0, help_text="卖五")
    sellFivePri = models.FloatField(default=0.00, help_text="卖五报价")
    date = models.DateTimeField("日期", null=True, help_text="日期")
    time = models.DateTimeField("时间", null=True, help_text="时间")

    dot = models.FloatField(default=0.00, help_text="当前价格")
    nowPic = models.FloatField(default=0.00, help_text="涨量")
    rate = models.FloatField(default=0.00, help_text="涨幅(%)")
    nowTraAmount = models.IntegerField(default=0, help_text="成交额(万)")
    nowTraNumber = models.IntegerField(default=0, help_text="成交量")

    minurl = models.CharField(max_length=200, default=None, help_text="分时K线图")
    dayurl = models.CharField(max_length=200, default=None, help_text="日K线图")
    weekurl = models.CharField(max_length=200, default=None, help_text="周K线图")
    monthurl = models.CharField(max_length=200, default=None, help_text="月K线图")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "stockDetail"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class ToDo(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    describe = models.TextField(default=None, help_text="待办描述")
    end_time = models.DateTimeField("截止时间", null=True, help_text="截止时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="", null=True, help_text="用户id")
    is_done = models.IntegerField(default=0, help_text="是否完成")  # 0 未完成 1 已完成 2 已过期
    is_home = models.BooleanField(default=False, help_text="是否展示到首页")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    class Meta:
        db_table = "to_do"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, help_text="消息内容")
    obj_id = models.CharField(max_length=50, null=True, help_text="对象ID")
    date = models.DateTimeField("写入时间", null=True, help_text="写入时间")
    is_look = models.BooleanField(default=False, help_text="是否已读")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    class Meta:
        db_table = "message"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()
