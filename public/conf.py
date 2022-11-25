#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: conf.py
# 创建时间: 2022/11/20 0020 12:47
# @Version：V 0.1
# @desc :
from datetime import date, datetime

# token
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 请求方式
GET = "GET"
POST = "POST"

# 分页
NumberOfPages = 10

# redis缓存key
# 诗词推荐
RECOMMEND = "RECOMMEND"
# 股票年k线
YearChart = "YearChart"
# 5天k线
FiveChart = "FiveChart"
# 10天k线
TenChart = "TenChart"

# 万年历KEY
CALENDAR_KEY = "197557d5fc1f3a26fa772bc694ea4c2d"

# 万年历成语接龙
IDIOM_KEY = "3b46a1f367b46094fcb766e56f76170f"

# 成语大全
IDIOM_INFO = "2f8b9617804af8aaedbc264b37c116aa"

# 天气
WEATHER_KEY = "4dd0557f59831bd698f8bb4a830145c4"

# 高德地图KEY
GAO_KEY = "b5b15bbd3252eb0cbb01877ae53a34d7"

# 北京 110000
# 顺义 110113
# 屯留 140405
# 长治 140400
# 太原 140100
# 城市代码
CITY_CODE = 110113

# 城市名称
CITY_NAME = "北京"

# 诗词类型
POETRY_TYPE = {
    "春天": 1, "夏天": 2, "秋天": 3, "冬天": 4, "爱国": 5, "写雪": 6, "思念": 7, "爱情": 8, "思乡": 9,
    "离别": 10, "月亮": 11, "梅花": 12, "励志": 13, "荷花": 14, "写雨": 15, "友情": 16, "感恩": 17,
    "写风": 18, "西湖": 19, "读书": 20, "菊花": 21, "长江": 22, "黄河": 23, "竹子": 24, "哲理": 25, "泰山": 26,
    "边塞": 27, "柳树": 28, "写鸟": 29, "桃花": 30, "老师": 31, "母亲": 32, "伤感": 33, "田园": 34,
    "写云": 35, "庐山": 36, "山水": 37, "星星": 38, "荀子": 39, "孟子": 40, "论语": 41,
    "墨子": 42, "老子": 43, "史记": 44, "中庸": 45, "礼记": 46, "尚书": 47, "晋书": 48, "左传": 49, "论衡": 50, "管子": 51,
    "说苑": 52, "列子": 53, "国语": 54, "节日": 55, "春节": 56, "元宵节": 57, "寒食节": 58, "清明节": 59, "端午节": 60, "七夕节": 61,
    "中秋节": 62, "重阳节": 63, "韩非子": 64, "菜根谭": 65, "红楼梦": 66, "弟子规": 67, "战国策": 68, "后汉书": 69, "淮南子": 70, "商君书": 71,
    "水浒传": 72, "格言联璧": 73, "围炉夜话": 74, "增广贤文": 75, "吕氏春秋": 76, "文心雕龙": 77, "醒世恒言": 78,
    "警世通言": 79, "幼学琼林": 80, "小窗幽记": 81, "三国演义": 82, "贞观政要": 83, "唐诗三百首": 84, "古诗三百首": 85, "宋词三百首": 86,
    "小学古诗文": 87, "初中古诗文": 88, "高中古诗文": 89, "宋词精选": 90, "古诗十九首": 91, "诗经": 92, "楚辞": 93, "乐府诗集精选": 94,
    "写景": 95, "咏物": 96, "写花": 97, "写山": 98, "写水": 99, "儿童": 100, "写马": 101, "地名": 102, "怀古": 103, "抒情": 104,
    "送别": 105, "闺怨": 106, "悼亡": 107, "写人": 108, "战争": 109, "惜时": 110, "忧民": 111, "婉约": 112, "豪放": 113, "民谣": 114,
}
