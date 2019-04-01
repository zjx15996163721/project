# -*- coding: utf-8 -*-
# @Time    : 2018/7/25 13:57
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : china.py
# @Software: PyCharm

from pymongo import MongoClient
import pika
import requests
from amap_reconfiguration.api_builder import ApiKey, api_key_list
import json

API_KEY_BUILDER = ApiKey()

client = MongoClient('114.80.150.198', 38888)
db = client['fangjia_base']
collection = db['city_bounds_box']

coll = db['china']


class China(object):
    def __init__(self):
        self.headers = {
            'Host': 'restapi.amap.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }

    def get_all_links(self):
        for i in collection.find({}):
            east = i['bound_gd'][0]
            north = i['bound_gd'][1]
            start_url='https://restapi.amap.com/v3/geocode/regeo?key={}&location={},{}&poitype=商务写字楼&radius=1000&extensions=all&batch=false&roadlevel=0'.format(next(API_KEY_BUILDER), east, north)
            try:
                response = requests.get(url=start_url, headers=self.headers)
                res = json.loads(response.text)
                addressComponent = res['regeocode']['addressComponent']
                country = addressComponent['country']
                if country == '中国':
                    coll.insert_one(i)
                    print('插入一条数据{}'.format(i))
                else:
                    print('不是中国')
            except Exception as e:
                print(e)

    def start_crawler(self):
        self.get_all_links()


if __name__ == '__main__':
    amap = China()
    amap.start_crawler()


















