# -*- coding: utf-8 -*-
# @Time    : 2018/8/14 21:13
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : count_consumer.py
# @Software: PyCharm
import requests
import pika
import json
import yaml
from pymongo import MongoClient
import gevent
from lib.proxy_iterator import Proxies
from multiprocessing import Process

s = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=s['mongo']['host'], port=s['mongo']['port'], username=s['mongo']['user_name'], password=s['mongo']['password'])
db = m['mongo']['db_name']
count_collection = db['dianping_count']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=s['rabbit']['host'], port=s['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='count_new')

p = Proxies()


def get_count(data):
    url = data['url']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    try:
        r = requests.get(url=url, headers=headers, proxies=next(p))
        if '没有找到合适的商户' in r.text:
            print('没有找到合适的商户')
        else:
            count = r.json()['recordCount']
            info = {
                'count': count,
                'city_id': data['city_id'],
                'city_name': data['city_name'],
                'region_id': data['region_id'],
                'region_name': data['region_name'],
                'second_categoryId': data['second_categoryId'],
                'second_category_name': data['second_category_name'],
            }
            count_collection.insert(info)
            print('插入一条数据 {}'.format(info))
    except Exception as e:
        print(e)


def callback(ch, method, properties, body):
    new_body = json.loads(body.decode())
    tasks = [gevent.spawn(get_count, data) for data in new_body]
    gevent.joinall(tasks)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def run():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='count_new')
    channel.start_consuming()


if __name__ == '__main__':
    for i in range(5):
        Process(target=run).start()

