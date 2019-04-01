# coding=gbk
import aiohttp
import asyncio
import json
from pymongo import MongoClient
from lib.log import LogHandler
log = LogHandler(__name__)
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_city_list = m['fangjiaguanjia']['city_list']
collection_price = m['fangjiaguanjia']['price']
for i in collection_price.find({'lease_price': None, 'sale_price': None}, no_cursor_timeout=True):
    print(i)

