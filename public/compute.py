#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: compute.py
# 创建时间: 2023/1/3 0003 21:54
# @Version：V 0.1
# @desc :
# import matplotlib.pyplot as plt
import baostock as bs
import pandas as pd
import talib as ta


def compute_kdj_and_macd(stock_code: str, start_date: str, end_date: str) -> tuple:
    """
    KDJ:
     >> KDJ 的计算比较复杂，首先要计算周期（n 日、n 周等）的 RSV 值，即未成熟随机指标
    值，然后再计算 K 值、D 值、J 值等。以 n 日 KDJ 数值的计算为例：
    （1）n 日 RSV=（Cn－Ln）/（Hn－Ln）×100
    公式中，Cn 为第 n 日收盘价；Ln 为 n 日内的最低价；Hn 为 n 日内的最高价。
    （2）其次，计算 K 值与 D 值：
    当日 K 值=2/3×前一日 K 值+1/3×当日 RSV
    当日 D 值=2/3×前一日 D 值+1/3×当日 K 值
    若无前一日 K 值与 D 值，则可分别用 50 来代替。
    （3）J 值=3*当日 K 值-2*当日 D 值
    KDJ 的基本使用方法：
    K 线是快速确认线——数值在 90 以上为超买，数值在 10 以下为超卖；
    D 线是慢速主干线——数值在 80 以上为超买，数值在 20 以下为超卖；
    J 线为方向敏感线，当 J 值大于 100，特别是连续 5 天以上，股价至少会形成短期头部，
    反之 J 值小于 0 时，特别是连续数天以上，股价至少会形成短期底部
    MACD:
    >> 计算公式如下：
    （1）首先，计算 EMA 的平滑系数
    平滑系数＝2÷（周期单位数＋1 ）
    如：12 日 EMA 的平滑系数＝2÷（12＋1）＝0．1538；
    26 日 EMA 平滑系数为=2÷27＝0．0741
    （2）然后，计算指数平均值（EMA）
    今天的指数平均值＝平滑系数×（今天收盘指数－昨天的指数平均值）＋昨天的指数平
    均值。
    依公式可计算出 12 日 EMA：
    12 日 EMA＝2÷13×（今天收盘指数一昨天的指数平均值）＋昨天的指数平均值。
    ＝（2÷13）×今天收盘指数＋（11÷13）×昨天的指数平均值。
    同理，26 日 EMA 亦可计算出：
    26 日 EMA＝（2÷27）×今天收盘指数＋（25÷27）×昨天的指数平均值。
    （3）计算离差值（DIF）
    DIF=今日 EMA（12）－今日 EMA（26）
    （4）最后，计算 DIF 的 9 日 EMA
    根据离差值计算其 9 日的 EMA，即离差平均值，是所求的 MACD 值。为了不与指标原
    名相混淆，此值又名 DEA 或 DEM（有时会成为 signal）。计算出的 DIF 和 DEA 的数值均为正
    值或负值。
    今日 DEA =前一日 DEA×8/10+今日 DIF×2/10
    >> 运用有如下基本原则：
    1.DIF、DEA 均为正，DIF 向上突破 DEA，买入信号参考。
    2.DIF、DEA 均为负，DIF 向下跌破 DEA，卖出信号参考。
    3.DIF 线与 K 线发生背离，行情可能出现反转信号。
    4.DIF、DEA 的值从正数变成负数，或者从负数变成正数并不是交易信号，因为它们落后
    于市场。
    简单地对应市场上的说法如下：
    1. MACD 金叉： DIF 由下向上突破 DEA，为买入信号。
    2. MACD 死叉： DIF 由上向下突破 DEA，为卖出信号。
    针对这两条的说法，我需要提出 MACD 具有一定的滞后情况，即比市场的反应要慢。因
    为 MACD 是一个中长期的指标，而不是个短期指标，不适合短期涨跌浮动太大的证券。
    接下来，3 种说法更靠谱些：
    3. MACD 柱状图为红，即 DIF 与 DEA 均为正值,即都在零轴线以上时，市场趋势属多头
    市场，若此时 DIF 向上继续突破 DEA，即红色柱状越来越长，可作买入信号，该出手就出
    手。
    4. MACD 柱状图为绿，即 DIF 与 DEA 均为负值,即都在零轴线以下时，市场趋势属空头
    市场，若此时 DIF 向下继续跌破 DEA，即绿色柱状越来越长，可作卖出信号，该割肉就割
    肉。
    5. 当 DEA 线与 K 线趋势发生背离时为反转信号。
    """
    bs.login()
    # 获取股票日k线数据
    rs = bs.query_history_k_data(stock_code,
                                 "date,code,high,close,low,tradeStatus",
                                 start_date=start_date,
                                 end_date=end_date,
                                 frequency="d", adjustflag="3")
    # 结果集
    result_list = list()
    while (rs.error_code == "0") & rs.next():
        # 获取一条数据，讲记录合并在一起
        result_list.append(rs.get_row_data())
    df_init = pd.DataFrame(result_list, columns=rs.fields)
    # 剔除停盘数据
    df_status = df_init[df_init["tradeStatus"] == "1"]

    # 获取 dif,dea,hist，它们的数据类似是 tuple，且跟 df2 的 date 日期一一对应
    # 记住了 dif,dea,hist 前 33 个为 Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    # 这里计算的 hist 就是 dif-dea,而很多证券商计算的 MACD=hist*2=(difdea)*2
    dif, dea, hist = ta.MACD(df_status['close'].astype(
        float).values, fastperiod=12, slowperiod=26, signalperiod=9)
    df_macd = pd.DataFrame({'dif': dif[33:], 'dea': dea[33:], 'hist': hist[33:]},
                           index=df_status['date'].iloc[33:], columns=['dif', 'dea', 'hist'])
    df_macd["time"] = df_status['date'].iloc[33:].values
    # 寻找 MACD 金叉和死叉
    datenumber = int(df_macd.shape[0])
    for i in range(datenumber - 1):
        if (df_macd.iloc[i, 0] <= df_macd.iloc[i, 1]) & (df_macd.iloc[i + 1, 0] >= df_macd.iloc[i + 1, 1]):
            df_macd.loc[df_macd["time"] == df_macd.index[i + 1], "MACD_金叉死叉"] = "金叉"
        if (df_macd.iloc[i, 0] >= df_macd.iloc[i, 1]) & (df_macd.iloc[i + 1, 0] <= df_macd.iloc[i + 1, 1]):
            df_macd.loc[df_macd["time"] == df_macd.index[i + 1], "MACD_金叉死叉"] = "死叉"

    low = df_status["low"].astype(float)
    del df_status["low"]
    df_status.insert(0, "low", low)
    high = df_status["high"].astype(float)
    del df_status["high"]
    df_status.insert(0, "high", high)
    close = df_status["close"].astype(float)
    del df_status["close"]
    df_status.insert(0, "close", close)
    # 计算KDJ指标，前9个数据为空
    low_list = df_status["low"].rolling(window=9).min()
    high_list = df_status["high"].rolling(window=9).max()

    rsv = (df_status["close"] - low_list) / (high_list - low_list) * 100
    df_kdj = pd.DataFrame()
    df_kdj["K"] = rsv.ewm(com=2).mean()
    df_kdj["D"] = df_kdj["K"].ewm(com=2).mean()
    df_kdj["J"] = 3 * df_kdj["K"] - 2 * df_kdj["D"]
    df_kdj["date"] = df_status["date"].values
    # df_data.index = df_status["date"].values
    # df_data.index.name = "index"
    # 删除空数据
    df_kdj = df_kdj.dropna()
    # 计算KDJ指标金叉和死叉
    df_kdj["KDJ_金叉死叉"] = ""
    kdj_position = df_kdj["K"] > df_kdj["D"]
    df_kdj.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, "KDJ_金叉死叉"] = "金叉"
    df_kdj.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, "KDJ_金叉死叉"] = "死叉"
    # 折线图
    # df_data.plot(title="KDJ")
    # plt.show()
    bs.logout()
    return df_kdj, df_macd


if __name__ == '__main__':
    code = "sz.002047"
    # code = "sh.601069"
    start_date = "2022-06-24"
    end_date = "2023-01-04"
    df_kdj, df_macd = compute_kdj_and_macd(code, start_date, end_date)
    df_kdj.to_csv(r"E:\projects\SuperNiubility\tools\2.csv", encoding="gbk")
    df_macd.to_csv(r"E:\projects\SuperNiubility\tools\3.csv", encoding="gbk")
