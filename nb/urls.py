#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: urls.py
# 创建时间: 2022/11/19 0019 21:34
# @Version：V 0.1
# @desc :
from django.urls import path

from nb import views, views_api, views_api_v1

urlpatterns = [
    path("do/", views.ToDOIndex.as_view(), name="todo"),
    path("do/add/", views.todo_add, name="todo_add"),
    path("do/edit/<uuid:todo_id>/", views.todo_edit, name="todo_edit"),
    path("do/look/<uuid:todo_id>/", views.todo_look, name="todo_look"),
    path("do/del/<uuid:todo_id>/", views.todo_del, name="todo_del"),
    path("do/done/<uuid:todo_id>/", views_api.todo_done, name="todo_done"),
    path("do/home/<uuid:todo_id>/", views_api.todo_home, name="todo_home"),
    path("do/<int:number>/", views_api.todo_find_number, name="todo_number"),

    path("stock/", views.StockIndex.as_view(), name="stock"),
    path("stock/add/", views.stock_add, name="stock_add"),
    path("stock/edit/<uuid:stock_id>/", views.stock_edit, name="stock_edit"),
    path("stock/look/<uuid:stock_id>/", views.stock_look, name="stock_look"),
    path("stock/chart/<uuid:stock_id>/", views.chart_look, name="chart_look"),
    path("stock/del/<uuid:stock_id>/", views.stock_del, name="stock_del"),
    path("stock/import/<uuid:hold_id>/", views_api.stock_import, name="stock_import"),
    path("stock/year/chart/", views_api.half_year_chart, name="half_year_chart"),
    path("stock/day/chart/", views_api.day_chart, name="day_chart"),
    path("stock/five/chart/", views_api.five_chart, name="five_chart"),
    path("stock/ten/chart/", views_api.ten_chart, name="ten_chart"),
    path("stock/twenty/chart/", views_api.twenty_chart, name="twenty_chart"),
    path("stock/buy/sell/", views_api.buy_sell_chart, name="buy_sell"),

    path("record/", views.RecordIndex.as_view(), name="record"),
    path("record/five/", views_api.record, name="record_five"),
    path("record/look/<int:record_id>/", views.record_look, name="record_look"),

    path("poetry/random/", views_api.recommend_poetry, name="poetry_random"),
    path("poetry/detail/<uuid:poetry_id>/", views_api.poetry_detail, name="poetry_detail"),

    path("message/", views_api.message_remind, name="message"),

    path("faker/<int:number>/", views_api_v1.get_faker, name="get_faker"),
]
