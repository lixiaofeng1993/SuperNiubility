#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: test.py
# 创建时间: 2022/12/14 0014 12:59
# @Version：V 0.1
# @desc :
import efinance as ef

# quotes = ef.stock.get_quote_snapshot("002047")
quotes = ef.stock.get_top10_stock_holder_info("002047", top=10)
# quotes = ef.stock.get_today_bill("002047")
# quotes = ef.stock.get_history_bill("002047")
# quotes = ef.stock.get_belong_board("002047")
quotes.to_csv("6.csv")
print(quotes)
