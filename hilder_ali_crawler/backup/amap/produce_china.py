# -*- coding: utf-8 -*-
# @Time    : 2018/7/25 13:57
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : china.py
# @Software: PyCharm

# from gevent import monkey
# monkey.patch_all()
# import gevent
from pymongo import MongoClient
import pika
import requests
from amap_reconfiguration.api_builder import ApiKey, api_key_list
import json

# API_KEY_BUILDER = ApiKey()

client = MongoClient('192.168.6.30', 27017)
db = client['fangjia_base']
collection = db['city_bounds_box']

# coll = db['china']


class China(object):
    def __init__(self):
        self.headers = {
            'Host': 'restapi.amap.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        self.connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection1.channel()
        self.channel.queue_declare(queue='china', durable=True)

    def get_all_links(self):
        new_list = []
        for i in collection.find({}):
            east = i['bound_gd'][0]
            north = i['bound_gd'][1]
            east_north = [east, north]
            new_list.append(east_north)
            if len(new_list) == 10:
                self.channel.basic_publish(exchange='',
                                          routing_key='china',
                                          body=json.dumps(new_list),
                                          properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化
                                        )
                print('[生产者] Send message {}'.format(new_list))
                new_list.clear()
            else:
                continue

    def start_crawler(self):
        self.get_all_links()


if __name__ == '__main__':
    amap = China()
    amap.start_crawler()

































