# -*- coding: utf-8 -*-
# @Time    : 2018/8/18 1:08
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : get_city_region_consumer.py
# @Software: PyCharm
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import pika
import json
import yaml

s = yaml.load(open('config_postcode.yaml'))
m = MongoClient(host=s['mongo']['host'], port=s['mongo']['port'], username=s['mongo']['user_name'], password=s['mongo']['password'])
db = m['postcode']
postcode_city_collection = db['postcode_all_city_new']
postcode_region_collection = db['postcode_all_region_new']
connection = pika.BlockingConnection(pika.ConnectionParameters(host=s['rabbit']['host'], port=s['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='postcode')


class Consumer(object):
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        self.proxies = proxies

    def get_info(self, url, province_name, city_name, region_name):
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            r_text = r.content.decode('gbk')
            soup = BeautifulSoup(r_text, 'lxml')
            info = soup.select('.table-list > tr > td')
            for i in range(0, len(info), 2):
                detail_postcode = info[i].text
                detail_name = info[i+1].text
                print(detail_postcode + ' ' + detail_name)
                data = {
                    'province_name': province_name,
                    'city_name': city_name,
                    'region_name': region_name,
                    'detail_name': detail_name,
                    'detail_postcode': detail_postcode
                }
                if postcode_region_collection.find_one({'province_name': province_name, 'city_name': city_name, 'region_name': region_name, 'detail_name': detail_name, 'detail_postcode': detail_postcode}) is None:
                    postcode_region_collection.insert_one(data)
                    print('插入一条数据 {}'.format(data))
                else:
                    print('已经存在库中')
        except Exception as e:
            print('请求失败,切换代理')

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        url = body['url']
        province_name = body['province_name']
        city_name = body['city_name']
        region_name = body['region_name']
        self.get_info(url, province_name, city_name, region_name)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='postcode')
        channel.start_consuming()

