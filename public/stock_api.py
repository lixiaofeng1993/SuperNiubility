#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: stock_api.py
# 创建时间: 2022/11/28 0028 18:48
# @Version：V 0.1
# @desc :
from nb.models import Shares, Shareholder, StockSector, StockSuper, StockKDJ, StockMACD, StockRSI
from public.views_com import *
from public.compute import compute_kdj_and_macd
from public.log import logger


def stock_today():
    """
    今日走势K线
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
                cache.delete(TodayChart.format(user_id=hold.user_id))
                cache.delete(TodayStockChart.format(stock_id=hold.id))
                message_writing(MessageToday.format(name=hold.name), hold.id, moment["today"], Chart)
            except Exception as error:
                logger.error(f"今日走势K线 更新持仓盈亏出现错误. ===>>> {error}")
                return
    if shares_list:
        try:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"今日走势K线 保存成功 ===>>> {len(shares_list)} 条")
        except Exception as error:
            logger.error(f"今日走势K线 保存失败 ===>>> {error}")


def stock_buy_sell(stock_id: str = ""):
    """
    买入卖出托单
    """
    if not stock_id:
        moment = check_stoke_date()
        if not moment:  # 判断股市开关时间
            return
        hold_list = SharesHold.objects.filter(is_delete=False)
        if not hold_list:
            logger.error("买入卖出托单 持仓 表数据为空.")
            return
    else:
        moment = etc_time()
        hold_list = SharesHold.objects.filter(Q(is_delete=False) & Q(id=stock_id))
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
        base_df = ef.stock.get_base_info(hold.code)
        if base_df.empty:
            logger.info(f"股票 {hold.name} 信息查询数据为空.")
        net_profit = base_df["净利润"] if base_df.get("净利润") else None
        total_market_value = base_df["总市值"] if base_df.get("总市值") else None
        circulation_market_value = base_df["流通市值"] if base_df.get("流通市值") else None
        industry = base_df["所处行业"] if base_df.get("所处行业") else None
        pe_ratio_dynamic = base_df["市盈率(动)"] if base_df.get("市盈率(动)") else None
        roe_ratio = base_df["ROE"] if base_df.get("ROE") else None
        gross_profit_margin = base_df["毛利率"] if base_df.get("毛利率") else None
        net_interest_rate = base_df["净利率"] if base_df.get("净利率") else None
        section_no = base_df["板块编号"] if base_df.get("板块编号") else None
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
            date=moment["today"], net_profit=net_profit, total_market_value=total_market_value,
            circulation_market_value=circulation_market_value, industry=industry, P_E_ratio_dynamic=pe_ratio_dynamic,
            ROE_ratio=roe_ratio, gross_profit_margin=gross_profit_margin, net_interest_rate=net_interest_rate,
            section_no=section_no,
        )
        detail_list.append(obj)
        if detail_list:
            is_profit = regularly_hold(hold, moment, quotes["最新价"], quotes["昨收"])
            if is_profit != hold.is_profit:
                profit_and_loss(hold)  # 钉钉消息提醒
            if quotes["最新价"] == quotes["涨停价"]:
                limit_up(hold, True)
            elif quotes["最新价"] == quotes["跌停价"]:
                limit_up(hold, False)
            if not stock_id:
                message_writing(MessageBuySell.format(name=hold.name), hold.id, moment["today"], Chart)
            cache.delete(TodayBuySellChart.format(stock_id=hold.id))
    if detail_list and not stock_id:
        try:
            StockDetail.objects.bulk_create(objs=detail_list)
            logger.info(f"买入卖出托单 保存成功 ===>>> {len(detail_list)} 条")
        except Exception as error:
            logger.error(f"买入卖出托单 保存失败 ===>>> {error}")


def stock_inflow():
    """
    资金流入流出
    """
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
            cache.delete(TodayInflowChart.format(stock_id=hold.id))
            message_writing(MessageInflow.format(name=hold.name), hold.id, moment["today"], Detail)
    if inflow_list:
        try:
            InflowStock.objects.bulk_create(objs=inflow_list)
            logger.info(f"资金流入流出 保存成功 ===>>> {len(inflow_list)}")
        except Exception as error:
            logger.error(f"资金流入流出 保存失败 ===>>> {error}条")


def stock_holder():
    """
    股票持仓十大股东数据变化
    """
    moment = check_stoke_day()
    if not moment:
        return
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
            message_writing(MessageHolder.format(name=hold.name), hold.id, moment["today"], Detail)
    if holder_list:
        try:
            Shareholder.objects.bulk_create(objs=holder_list)
            logger.info(f"持仓股东数据 保存成功 ===>>> {len(holder_list)}条")
        except Exception as error:
            logger.error(f"持仓股东数据 保存失败 ===>>> {error}")


def stock_holder_number():
    """
    持仓股东数量数据变化
    """
    moment = check_stoke_day()
    if not moment:
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("持仓股东数量数据 持仓 表数据为空.")
        return
    holder_list = list()
    for hold in hold_list:
        holder = ShareholderNumber.objects.filter(
            Q(code=hold.code) & Q(shares_hold_id=hold.id)).order_by("-end_time").first()
        if holder:
            base_date_time = str(holder.end_time)
        else:
            base_date_time = ""
        df = ef.stock.get_latest_holder_number()
        if df.empty:
            logger.error(f"持仓股东数量数据 股票 {hold.name} 查询数据为空.")
            return
        df_list = df.to_dict(orient="records")
        for data in df_list:
            if hold.code == data["股票代码"]:
                date_time = data["股东户数统计截止日"]
                if base_date_time and date_time <= base_date_time:  # 避免重复写入
                    continue
                obj = ShareholderNumber(
                    name=data["股票名称"], code=data["股票代码"], holder_number=data["股东人数"], fluctuate=data["股东人数增减"],
                    diff_rate=data["较上期变化百分比"], end_time=data["股东户数统计截止日"], avg_amount=data["户均持股市值"],
                    avg_number=data["户均持股数量"], total_amount=data["总市值"], total_price=data["总股本"],
                    notice_date=data["公告日期"], shares_hold_id=hold.id
                )
                holder_list.append(obj)
        if holder_list:
            message_writing(MessageHolderNumber.format(name=hold.name), hold.id, moment["today"], Detail)
    if holder_list:
        try:
            ShareholderNumber.objects.bulk_create(objs=holder_list)
            logger.info(f"持仓股东数量数据 保存成功 ===>>> {len(holder_list)}条")
        except Exception as error:
            logger.error(f"持仓股东数量数据 保存失败 ===>>> {error}")


def stock_sector():
    """
    股票所属板块涨跌数据
    """
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
        if not sector:
            logger.error("查询股票板块表数据为空.")
            return
        update_date = sector.update_date
        seconds = (moment["now"] - update_date).total_seconds()
        if seconds <= 300 or update_date > moment["stock_time"]:
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
            message_writing(MessageSector.format(name=hold.name), hold.id, moment["today"], Detail)
    if sector_list:
        try:
            StockSector.objects.bulk_create(objs=sector_list)
            logger.info(f"所属板块数据 保存成功 ===>>> {len(sector_list)}条")
        except Exception as error:
            logger.error(f"所属板块数据 保存失败 ===>>> {error}")


def stock_super():
    """
    龙虎榜数据
    """
    moment = check_stoke_day()
    if not moment:
        return
    holder = StockSuper.objects.filter(is_delete=False).order_by("-time").first()
    if holder:
        base_date_time = str(holder.time).split(" ")[0]
    else:
        base_date_time = ""
    df = ef.stock.get_daily_billboard()
    if df.empty:
        logger.error(f"龙虎榜查询数据为空.")
        return
    df = df.where(df.notnull(), 0)
    df_list = df.to_dict(orient="records")
    super_list = list()
    for data in df_list:
        date_time = data["上榜日期"]
        if base_date_time and date_time <= base_date_time:  # 避免重复写入
            continue
        hold = SharesHold.objects.filter(code=data["股票代码"]).first()
        hod_id = hold.id if hold else None
        obj = StockSuper(
            name=data["股票名称"], code=data["股票代码"], time=data["上榜日期"], unscramble=data["解读"], open_price=data["收盘价"],
            rise_rate=data["涨跌幅"], turnover_rate=data["换手率"], net_purchase_amount=data["龙虎榜净买额"],
            purchase_amount=data["龙虎榜买入额"], sales_amount=data["龙虎榜卖出额"], turnover_amount=data["龙虎榜成交额"],
            total_turnover_amount=data["市场总成交额"], net_purchases_rate=data["净买额占总成交比"],
            net_turnover_rate=data["成交额占总成交比"], market_equity=data["流通市值"], reason=data["上榜原因"], shares_hold_id=hod_id
        )
        super_list.append(obj)
    if super_list:
        try:
            StockSuper.objects.bulk_create(objs=super_list)
            logger.info(f"龙虎榜 保存成功 ===>>> {len(super_list)}条")
            message_writing(MessageDragon.format(name="龙虎榜"), "", moment["today"], Dragon)
        except Exception as error:
            logger.error(f"龙虎榜 保存失败 ===>>> {error}")


def stock_deal():
    """
    获取股票最新交易日成交明细
    """
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("成交明细 持仓 表数据为空.")
        return
    detail_list = list()
    for hold in hold_list:
        detail = ef.stock.get_deal_detail(hold.code)
        if detail.empty:
            logger.error(f"成交明细 股票 {hold.name} 查询数据为空.")
            continue
        df_list = detail.to_dict(orient="records")
        for df in df_list:
            date_time = f"{moment['today']} {df['时间']}"
            deal = StockDeal.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id) & Q(time=date_time)).exists()
            if deal:
                continue
            obj = StockDeal(
                code=df["股票代码"], name=df["股票名称"], time=date_time, old_price=df["昨收"],
                deal_price=df["成交价"], deal_number=df["成交量"], singular=df["单数"], shares_hold_id=hold.id
            )
            detail_list.append(obj)
        if detail_list:
            message_writing(MessageDeal.format(name=hold.name), hold.id, moment["today"], Detail)
    if detail_list:
        try:
            StockDeal.objects.bulk_create(objs=detail_list)
            logger.info(f"成交明细 保存成功 ===>>> {len(detail_list)} 条")
        except Exception as error:
            logger.error(f"成交明细 保存失败 ===>>> {error}")


def stock_kdj_and_macd(start_date: str = "2022-06-24"):
    """
    股票KDJ、MACD、RSI数据
    """
    moment = check_stoke_day()
    if not moment:
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    if not hold_list:
        logger.error("股票KDJ、MACD、RSI数据 持仓 表数据为空.")
        return
    kdj_list = list()
    macd_list = list()
    rsi_list = list()
    end_date = str(moment["today"])
    for hold in hold_list:
        df_kdj, df_macd, df_rsi = compute_kdj_and_macd(difference_stock(hold.code), start_date, end_date)
        df_kdj = df_kdj.where(df_kdj.notnull(), "")
        df_macd = df_macd.where(df_macd.notnull(), "")
        df_rsi = df_rsi.where(df_rsi.notnull(), "")
        if df_kdj.empty:
            logger.error(f"股票 {hold.name} kdj数据 查询数据为空.")
            continue
        df_kdj_list = df_kdj.to_dict(orient="records")
        for df in df_kdj_list:
            date_time = f"{df['date']} 00:00:00"
            kdj = StockKDJ.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id) & Q(time=date_time)).exists()
            if kdj:
                continue
            obj = StockKDJ(
                name=hold.name, k=df["K"], d=df["D"], j=df["J"], time=date_time, type=df["KDJ_金叉死叉"],
                shares_hold_id=hold.id
            )
            kdj_list.append(obj)
        if kdj_list:
            cache.delete(TodayKDJChart.format(stock_id=hold.id))
            message_writing(MessageKDJ.format(name=hold.name), hold.id, moment["today"], Chart)
        if df_macd.empty:
            logger.error(f"股票 {hold.name} MACD数据 查询数据为空.")
            continue
        df_macd_list = df_macd.to_dict(orient="records")
        for df in df_macd_list:
            date_time = f"{df['time']} 00:00:00"
            kdj = StockMACD.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id) & Q(time=date_time)).exists()
            if kdj:
                continue
            obj = StockMACD(
                name=hold.name, dif=df["dif"], dea=df["dea"], macd=df["hist"], time=date_time, type=df["MACD_金叉死叉"],
                shares_hold_id=hold.id
            )
            macd_list.append(obj)
        if macd_list:
            cache.delete(TodayMACDChart.format(stock_id=hold.id))
            message_writing(MessageMACD.format(name=hold.name), hold.id, moment["today"], Chart)
        if df_rsi.empty:
            logger.error(f"股票 {hold.name} RSI数据 查询数据为空.")
            continue
        df_rsi_list = df_rsi.to_dict(orient="records")
        for df in df_rsi_list:
            date_time = f"{df['date']} 00:00:00"
            rsi = StockRSI.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id) & Q(time=date_time)).exists()
            if rsi:
                continue
            rsi1 = df["rsi_6days"] if df["rsi_6days"] else 0
            rsi2 = df["rsi_12days"] if df["rsi_12days"] else 0
            rsi3 = df["rsi_24days"] if df["rsi_24days"] else 0
            obj = StockRSI(
                name=hold.name, rsi1=rsi1, rsi2=rsi2, rsi3=rsi3, time=date_time,
                type=df["rsi_超买超卖"], shares_hold_id=hold.id, close=df["close"]
            )
            rsi_list.append(obj)
        if rsi_list:
            cache.delete(TodayRSIChart.format(stock_id=hold.id))
            message_writing(MessageRSI.format(name=hold.name), hold.id, moment["today"], Chart)
    if kdj_list:
        try:
            StockKDJ.objects.bulk_create(objs=kdj_list)
            logger.info(f"股票kdj数据 保存成功 ===>>> {len(kdj_list)} 条")
        except Exception as error:
            logger.error(f"股票kdj数据 保存失败 ===>>> {error}")
    if macd_list:
        try:
            StockMACD.objects.bulk_create(objs=macd_list)
            logger.info(f"股票MACD数据 保存成功 ===>>> {len(macd_list)} 条")
        except Exception as error:
            logger.error(f"股票MACD数据 保存失败 ===>>> {error}")
    if rsi_list:
        try:
            StockRSI.objects.bulk_create(objs=rsi_list)
            logger.info(f"股票RSI数据 保存成功 ===>>> {len(rsi_list)} 条")
        except Exception as error:
            logger.error(f"股票RSI数据 保存失败 ===>>> {error}")


if __name__ == '__main__':
    stock_inflow()
