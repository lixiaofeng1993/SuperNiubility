#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: stock_api.py
# 创建时间: 2022/11/28 0028 18:48
# @Version：V 0.1
# @desc :
import efinance as ef

from nb.models import Shares, StockDetail, InflowStock, Shareholder, StockSector
from public.send_ding import profit_and_loss, profit_and_loss_ratio, limit_up
from public.common import *
from public.log import logger


def stock_today():
    """
    持仓股票当天数据自动写入
    每五分钟写入一次
    """
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("今日走势K线 持仓 表数据为空.")
        return
    stock_list = list()
    stock_dict = dict()
    for hold in hold_list:
        stock_list.append(hold.code)
        stock_dict.update({hold.code: hold.id})
    freq = 1
    df = ef.stock.get_quote_history(stock_list, klt=freq)
    if not df:
        logger.error(f"今日走势K线 股票 {stock_list} 查询数据为空.")
        return
    shares_list = []
    for key, value in df.items():
        shares = Shares.objects.filter(
            Q(code=key) & Q(shares_hold_id=stock_dict[key])).order_by("-date_time").first()
        if not shares:
            logger.error(f"今日走势K线 股票 {stock_list} 请先导入 Shares 表数据.")
            return
        base_date_time = shares.date_time
        df_list = value.to_dict(orient="records")
        new_price = 0
        for data in df_list:
            date_time = data["日期"]
            if date_time <= base_date_time:  # 避免重复写入
                continue
            obj = Shares(
                name=data["股票名称"], code=key, date_time=data["日期"], open_price=data["开盘"],
                new_price=data["收盘"], top_price=data["最高"], down_price=data["最低"], turnover=data["成交量"],
                business_volume=data["成交额"], amplitude=data["振幅"], rise_and_fall=data["涨跌幅"],
                rise_and_price=data["涨跌额"], turnover_rate=data["换手率"], shares_hold_id=stock_dict[key]
            )
            new_price = data["收盘"]
            shares_list.append(obj)
        if new_price:
            try:
                hold = SharesHold.objects.get(id=stock_dict[key])
                is_profit = regularly_hold(hold, moment, new_price)
                if is_profit != hold.is_profit:
                    profit_and_loss(hold)  # 钉钉消息提醒
                if hold.cost_price:
                    profit_and_loss_ratio(hold, new_price)
                message_writing(MessageToday.format(name=hold.name), hold.user_id, hold.id, moment["today"], Chart)
            except Exception as error:
                logger.error(f"今日走势K线 更新持仓盈亏出现错误. ===>>> {error}")
                return
    if shares_list:
        try:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"今日走势K线 保存成功===>>>{len(shares_list)} 条")
            return hold_list
        except Exception as error:
            logger.error(f"今日走势K线 保存失败 ===>>> {error}")


def stock_buy_sell():
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("买入卖出托单 持仓 表数据为空.")
        return
    detail_list = list()
    for hold in hold_list:
        quotes = ef.stock.get_quote_snapshot(hold.code)
        if quotes.empty:
            logger.error(f"买入卖出托单 股票 {hold.name} 查询数据为空.")
            continue
        quotes = quotes.where(quotes.notnull(), 0)
        date_time = f"{moment['today']} {quotes['时间']}"
        detail = StockDetail.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id) & Q(time=date_time)).exists()
        if detail:
            logger.info(f"买入卖出托单 股票 {hold.name} 当前时间 {date_time} 查询数据重复.")
            continue
        obj = StockDetail(
            code=quotes["代码"], name=quotes["名称"], time=date_time, increPer=quotes["涨跌幅"], increase=quotes["涨跌额"],
            nowPri=quotes["最新价"], yestodEndPri=quotes["昨收"], todayStartPri=quotes["今开"], todayMax=quotes["最高"],
            todayMin=quotes["最低"], avg_price=quotes["均价"], top_price=quotes["涨停价"], down_price=quotes["跌停价"],
            turnover_rate=quotes["换手率"], traNumber=quotes["成交量"], traAmount=quotes["成交额"], sellOnePri=quotes["卖1价"],
            sellTwoPri=quotes["卖2价"], sellThreePri=quotes["卖3价"], sellFourPri=quotes["卖4价"], sellFivePri=quotes["卖5价"],
            buyOnePri=quotes["买1价"], buyTwoPri=quotes["买2价"], buyThreePri=quotes["买3价"], buyFourPri=quotes["买4价"],
            buyFivePri=quotes["买5价"], sellOne=quotes["卖1数量"], sellTwo=quotes["卖2数量"], sellThree=quotes["卖3数量"],
            sellFour=quotes["卖4数量"], sellFive=quotes["卖5数量"], buyOne=quotes["买1数量"], buyTwo=quotes["买2数量"],
            buyThree=quotes["买3数量"], buyFour=quotes["买4数量"], buyFive=quotes["买5数量"], shares_hold_id=hold.id,
            date=moment["today"]
        )
        detail_list.append(obj)
        if detail_list:
            message_writing(MessageBuySell.format(name=hold.name), hold.user_id, hold.id, moment["today"], Chart)
            if quotes["最新价"] == quotes["涨停价"]:
                limit_up(hold, True)
            elif quotes["最新价"] == quotes["跌停价"]:
                limit_up(hold, False)
    if detail_list:
        try:
            StockDetail.objects.bulk_create(objs=detail_list)
            logger.info(f"买入卖出托单 保存成功===>>>{len(detail_list)} 条")
            return hold_list
        except Exception as error:
            logger.error(f"买入卖出托单 保存失败 ===>>> {error}")
            return


def stock_inflow():
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("资金流入流出 持仓 表数据为空.")
        return
    inflow_list = list()
    for hold in hold_list:
        inflow = InflowStock.objects.filter(
            Q(code=hold.code) & Q(shares_hold_id=hold.id)).order_by("-time", "-date").first()
        if inflow:
            base_date_time = str(inflow.time) if inflow.time else None
            base_date = str(inflow.date).split(" ")[0] if inflow.date else None
            df = ef.stock.get_today_bill(hold.code)
        else:
            base_date_time, base_date = "", ""
            df = ef.stock.get_history_bill(hold.code)
        if df.empty:
            logger.error(f"资金流入流出数据 股票 {hold.name} 查询数据为空.")
            return
        df_list = df.to_dict(orient="records")
        for data in df_list:
            date_time = data.get("时间")
            if date_time:
                if base_date_time and date_time <= base_date_time:  # 避免重复写入
                    continue
                if base_date and not base_date_time and str(moment["today"]) == base_date:
                    continue
                _date = date_time.split(" ")[0]
                _time = date_time
            else:
                date_time = data["日期"]
                _time = None
                _date = date_time
            obj = InflowStock(
                name=data["股票名称"], code=data["股票代码"], time=_time, main_inflow=data["主力净流入"],
                small_inflow=data["小单净流入"], middle_inflow=data["中单净流入"], big_inflow=data["大单净流入"],
                huge_inflow=data["超大单净流入"], shares_hold_id=hold.id, date=_date
            )
            inflow_list.append(obj)
        if inflow_list:
            message_writing(MessageInflow.format(name=hold.name), hold.user_id, hold.id, moment["today"], Detail)
    if inflow_list:
        try:
            InflowStock.objects.bulk_create(objs=inflow_list)
            logger.info(f"资金流入流出 保存成功！===>>> {len(inflow_list)}")
            return hold_list
        except Exception as error:
            logger.error(f"资金流入流出 保存失败 ===>>> {error}条")


def stock_holder():
    moment = check_stoke_date()
    # if not moment:  # 判断股市开关时间
    #     return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("持仓股东数据 持仓 表数据为空.")
        return
    holder_list = list()
    for hold in hold_list:
        holder = Shareholder.objects.filter(
            Q(code=hold.code) & Q(shares_hold_id=hold.id)).order_by("-time").first()
        if holder:
            base_date_time = str(holder.time).split(" ")[0]
            df = ef.stock.get_top10_stock_holder_info(hold.code, top=1)
        else:
            base_date_time = ""
            df = ef.stock.get_top10_stock_holder_info(hold.code, top=10)
        if df.empty:
            logger.error(f"持仓股东数据 股票 {hold.name} 查询数据为空.")
            return
        df_list = df.to_dict(orient="records")
        for data in df_list:
            date_time = data["更新日期"]
            if base_date_time and date_time <= base_date_time:  # 避免重复写入
                continue
            date_time = date_time.split(" ")[0]
            hold_rate = data["持股比例"].strip("%")
            obj = Shareholder(
                name=hold.name, code=data["股票代码"], time=date_time, holder_code=data["股东代码"],
                holder_name=data["股东名称"], hold_number=data["持股数"], hold_rate=hold_rate,
                fluctuate=data["增减"], fluctuate_rate=data["变动率"], shares_hold_id=hold.id
            )
            holder_list.append(obj)
        if holder_list:
            message_writing(MessageHolder.format(name=hold.name), hold.user_id, hold.id, moment["today"], Detail)
    if holder_list:
        try:
            Shareholder.objects.bulk_create(objs=holder_list)
            logger.info(f"持仓股东数据 保存成功！===>>> {len(holder_list)}条")
            return hold_list
        except Exception as error:
            logger.error(f"持仓股东数据 保存失败 ===>>> {error}")


def stock_sector():
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("所属板块数据 持仓 表数据为空.")
        return
    sector_list = list()
    for hold in hold_list:
        sector = StockSector.objects.filter(
            Q(code=hold.code) & Q(shares_hold_id=hold.id)).order_by("-update_date").first()
        if sector:
            update_date = sector.update_date
        else:
            update_date = ""
        if update_date:
            seconds = (moment["now"] - update_date).total_seconds()
            if seconds <= 300:
                logger.info(f"所属板块数据 剩余更新时间 {300 - seconds}秒")
                return
        df = ef.stock.get_belong_board(hold.code)
        if df.empty:
            logger.error(f"所属板块数据 股票 {hold.name} 查询数据为空.")
            return
        df_list = df.to_dict(orient="records")
        for data in df_list:
            obj = StockSector(
                name=data["股票名称"], code=data["股票代码"], sector_code=data["板块代码"], sector_name=data["板块名称"],
                sector_rate=data["板块涨幅"], shares_hold_id=hold.id
            )
            sector_list.append(obj)
        if sector_list:
            message_writing(MessageSector.format(name=hold.name), hold.user_id, hold.id, moment["today"], Detail)
    if sector_list:
        try:
            StockSector.objects.bulk_create(objs=sector_list)
            logger.info(f"所属板块数据 保存成功！===>>> {len(sector_list)}条")
            return hold_list
        except Exception as error:
            logger.error(f"所属板块数据 保存失败 ===>>> {error}")


if __name__ == '__main__':
    stock_inflow()
