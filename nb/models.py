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


class Shares(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, help_text="股票名称")
    code = models.CharField(max_length=20, null=False, help_text="股票代码")
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

    class Meta:
        db_table = "shares"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class ToDo(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    describe = models.TextField(default=None, help_text="待办描述")
    end_time = models.DateTimeField("截止时间", null=True, help_text="截止时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="", null=True, help_text="用户id")
    is_done = models.IntegerField(default=0, help_text="是否完成")  # 0 未完成 1 已完成 2 已过期
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    class Meta:
        db_table = "to_do"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()
