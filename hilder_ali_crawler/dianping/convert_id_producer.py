# -*- coding: utf-8 -*-
# @Time    : 2018/8/16 15:36
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : convert_id.py
# @Software: PyCharm
from pymongo import MongoClient
import pika
import json
import yaml

setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='dianping_no_id')


def find_no_id():
    for i in dianping_all_type_collection.find({"id": {'$exists': False}}, no_cursor_timeout=True):
        _id = str(i['_id'])
        i.pop('_id')
        i.update({'_id': _id})
        channel.basic_publish(exchange='',
                              routing_key='dianping_no_id',
                              body=json.dumps(i))
        print("放队列 {}".format(i))
