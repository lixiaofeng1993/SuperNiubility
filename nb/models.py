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
    """
    持仓股票
    """
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
    """
    股票详情
    """
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
    """
    股票卖出买入托单
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    increPer = models.FloatField(default=0.00, help_text="涨跌百分比")
    increase = models.FloatField(default=0.00, help_text="涨跌额")
    todayStartPri = models.FloatField(default=0.00, help_text="今日开盘价")
    yestodEndPri = models.FloatField(default=0.00, help_text="昨日收盘价")
    top_price = models.FloatField(default=0.00, help_text="涨停价")
    down_price = models.FloatField(default=0.00, help_text="跌停价")
    avg_price = models.FloatField(default=0.00, help_text="平均价")
    turnover_rate = models.FloatField(default=0.00, help_text="换手率")
    nowPri = models.FloatField(default=0.00, help_text="当前价格")
    todayMax = models.FloatField(default=0.00, help_text="今日最高价")
    todayMin = models.FloatField(default=0.00, help_text="今日最低价")
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

    net_profit = models.FloatField(default=0.00, help_text="净利润")
    total_market_value = models.FloatField(default=0.00, help_text="总市值")
    circulation_market_value = models.FloatField(default=0.00, help_text="流通市值")
    industry = models.CharField(max_length=20, default=None, help_text="所处行业")
    P_E_ratio_dynamic = models.FloatField(default=0.00, help_text="市盈率(动)")
    ROE_ratio = models.FloatField(default=0.00, help_text="净资产收益率")
    gross_profit_margin = models.FloatField(default=0.00, help_text="毛利率")
    net_interest_rate = models.FloatField(default=0.00, help_text="净利率")
    section_no = models.CharField(max_length=20, default=None, help_text="板块编号")

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
    """
    待办
    """
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
    """
    消息
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, help_text="消息内容")
    obj_id = models.CharField(max_length=50, null=True, help_text="对象ID")
    type = models.CharField(max_length=20, null=True, help_text="跳转页面")
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


class KDJStock(models.Model):
    """
    kdj
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    k = models.FloatField(default=0.00, help_text="k值")
    d = models.FloatField(default=0.00, help_text="d值")
    j = models.FloatField(default=0.00, help_text="j值")
    t = models.DateTimeField("时间", null=True, help_text="时间")
    name = models.CharField(max_length=20, null=False, help_text="股票名称")
    type = models.CharField(max_length=20, null=False, help_text="分时级别")
    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)
    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "kdj_stock"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class Shareholder(models.Model):
    """
    股票股东
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    time = models.DateTimeField("信息更新时间", null=True, help_text="信息更新时间")
    holder_code = models.CharField(max_length=50, default=None, help_text="股东代码")
    holder_name = models.CharField(max_length=200, default=None, help_text="股东名称")
    hold_number = models.CharField(max_length=50, default=None, help_text="持股数")
    hold_rate = models.FloatField(default=0.00, help_text="持股比例")
    fluctuate = models.CharField(max_length=50, default=None, help_text="增减")
    fluctuate_rate = models.CharField(max_length=50, default=None, help_text="变动率")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "shareholder"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class ShareholderNumber(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    holder_number = models.FloatField(default=0.00, help_text="股东人数")
    fluctuate = models.FloatField(default=0.00, help_text="股东人数增减")
    diff_rate = models.FloatField(default=0.00, help_text="较上期变化百分比")
    end_time = models.DateTimeField("股东户数统计截止日", null=True, help_text="股东户数统计截止日")
    avg_amount = models.FloatField(default=0.00, help_text="户均持股市值")
    avg_number = models.FloatField(default=0.00, help_text="户均持股数量")
    total_amount = models.FloatField(default=0.00, help_text="总市值")
    total_price = models.FloatField(default=0.00, help_text="总股本")
    notice_date = models.DateTimeField("公告日期", null=True, help_text="公告日期")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "shareholder_number"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class InflowStock(models.Model):
    """
    资金流入流出
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    time = models.DateTimeField("时间", null=True, help_text="时间")
    date = models.DateTimeField("日期", null=True, help_text="日期")
    main_inflow = models.FloatField(default=0.00, help_text="主力净流入")
    small_inflow = models.FloatField(default=0.00, help_text="小单净流入")
    middle_inflow = models.FloatField(default=0.00, help_text="中单净流入")
    big_inflow = models.FloatField(default=0.00, help_text="大单净流入")
    huge_inflow = models.FloatField(default=0.00, help_text="超大单净流入")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "inflow_stock"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class StockSector(models.Model):
    """
    股票板块
    """
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    sector_code = models.CharField(max_length=20, default=None, help_text="板块代码")
    sector_name = models.CharField(max_length=20, default=None, help_text="板块名称")
    sector_rate = models.FloatField(default=0.00, help_text="板块涨幅")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "stock_sector"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class StockSuper(models.Model):
    id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, default=None, help_text="股票名称")
    code = models.CharField(max_length=20, default=None, help_text="股票代码")
    time = models.DateTimeField("上榜日期", null=True, help_text="上榜日期")
    unscramble = models.CharField(max_length=200, default=None, help_text="解读")
    open_price = models.FloatField(default=0.00, help_text="收盘价")
    rise_rate = models.FloatField(default=0.00, help_text="涨跌幅")
    turnover_rate = models.FloatField(default=0.00, help_text="换手率")
    net_purchase_amount = models.FloatField(default=0.00, help_text="龙虎榜净买额")
    purchase_amount = models.FloatField(default=0.00, help_text="龙虎榜买入额")
    sales_amount = models.FloatField(default=0.00, help_text="龙虎榜卖出额")
    turnover_amount = models.FloatField(default=0.00, help_text="龙虎榜成交额")
    total_turnover_amount = models.FloatField(default=0.00, help_text="市场总成交额")
    net_purchases_rate = models.FloatField(default=0.00, help_text="净买额占总成交比")
    net_turnover_rate = models.FloatField(default=0.00, help_text="成交额占总成交比")
    market_equity = models.FloatField(default=0.00, help_text="流通市值")
    reason = models.CharField(max_length=200, default=None, help_text="上榜原因")

    is_delete = models.BooleanField(default=False, help_text="是否删除")
    update_date = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    create_date = models.DateTimeField("保存时间", default=timezone.now)

    shares_hold = models.ForeignKey(SharesHold, on_delete=models.CASCADE, default="", null=True, help_text="持仓股票ID")

    class Meta:
        db_table = "stock_super"

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()
