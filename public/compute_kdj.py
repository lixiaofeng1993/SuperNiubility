#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: compute_kdj.py
# 创建时间: 2023/1/3 0003 21:54
# @Version：V 0.1
# @desc :
# import matplotlib.pyplot as plt
import baostock as bs
import pandas as pd


def compute_kdj(stock_code: str, start_date: str, end_date: str):
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
    df_data = pd.DataFrame()
    df_data["K"] = rsv.ewm(com=2).mean()
    df_data["D"] = df_data["K"].ewm(com=2).mean()
    df_data["J"] = 3 * df_data["K"] - 2 * df_data["D"]
    df_data["date"] = df_status["date"].values
    # df_data.index = df_status["date"].values
    # df_data.index.name = "index"
    # 删除空数据
    df_data = df_data.dropna()
    # 计算KDJ指标金叉和死叉
    df_data["KDJ_金叉死叉"] = ""
    kdj_position = df_data["K"] > df_data["D"]
    df_data.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, "KDJ_金叉死叉"] = "金叉"
    df_data.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, "KDJ_金叉死叉"] = "死叉"
    # 折线图
    # df_data.plot(title="KDJ")
    # plt.show()
    bs.logout()
    return df_data


if __name__ == '__main__':
    code = "sz.002047"
    # code = "sh.601069"
    start_date = "2022-06-24"
    end_date = "2023-01-03"
    df = compute_kdj(code, start_date, end_date)
    df.to_csv(r"E:\projects\SuperNiubility\tools\2.csv", encoding="gbk")
