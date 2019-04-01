# -*- coding: utf-8 -*-
# @Time    : 2018/7/25 13:57
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : china.py
# @Software: PyCharm

from gevent import monkey
monkey.patch_all()
import gevent
from pymongo import MongoClient
import pika
import requests
from amap_reconfiguration.api_builder import ApiKey, api_key_list
import json

API_KEY_BUILDER = ApiKey()

client = MongoClient('192.168.6.30', 27017)
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
        self.connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection1.channel()
        self.channel.queue_declare(queue='china1', durable=True)

    def get_all_links(self, east_north):
        east = east_north[0]
        north = east_north[1]
        start_url = 'https://restapi.amap.com/v3/geocode/regeo?key={}&location={},{}&poitype=&radius=&extensions=all&batch=false&roadlevel='.format(next(API_KEY_BUILDER), east, north)
        try:
            response = requests.get(url=start_url, headers=self.headers)
            res = json.loads(response.text)
            addressComponent = res['regeocode']['addressComponent']
            country = addressComponent['country']
            if country == '中国':
                data = {
                    '经度': east,
                    '纬度': north
                }
                coll.insert_one(data)
                print('插入一条数据{}'.format(data))
            else:
                print('不是中国')
        except Exception as e:
            print(start_url)

    def callback(self,ch,method,properties,body):
        new_body = json.loads(body.decode())
        tasks = [gevent.spawn(self.get_all_links, east_north) for east_north in new_body]
        gevent.joinall(tasks)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='china1')
        self.channel.start_consuming()

    def start_crawler(self):
        self.consume_start()


if __name__ == '__main__':
    china = China()
    china.start_crawler()





