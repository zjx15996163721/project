# -*- coding: utf-8 -*-
# @Time    : 2018/8/14 15:48
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : count_producer.py
# @Software: PyCharm

import requests
import pika
import json
from dianping.category_orm import City, get_sqlalchemy_session, Region, Category, SecondCategory, ThirdCategory
import yaml
from pymongo import MongoClient

s = yaml.load(open('config_dianping.yaml'))
db_session = get_sqlalchemy_session()
m = MongoClient(host=s['mongo']['host'], port=s['mongo']['port'], username=s['mongo']['user_name'], password=s['mongo']['password'])
db = m['dianping']
count_collection = db['dianping_count']

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='count_new')


def run():
    data_list = []
    for city in db_session.query(City):
        city_id = city.city_id
        city_name = city.name
        region_list = db_session.query(Region).filter_by(city_id=city_id).all()
        for region in region_list:
            region_id = region.region_id
            region_name = region.name
            second_category_list = db_session.query(SecondCategory).filter_by(cityId=city_id).all()
            for second_category in second_category_list:
                second_categoryId = second_category.second_categoryId
                second_category_name = second_category.name
                url = 'https://mapi.dianping.com/searchshop.json?start=0&categoryid={}&limit=50&cityid={}&regionid={}'.format(second_categoryId, city_id, region_id)
                data = {
                    'city_id': city_id,
                    'city_name': city_name,
                    'region_id': region_id,
                    'region_name': region_name,
                    'second_categoryId': second_categoryId,
                    'second_category_name': second_category_name,
                    'url': url
                }
                data_list.append(data)
                if len(data_list) == 100:
                    channel.basic_publish(exchange='',
                                          routing_key='count_new',
                                          body=json.dumps(data_list))
                    print('放队列 {}'.format(data_list))
                    data_list.clear()
                else:
                    continue
    channel.basic_publish(exchange='',
                          routing_key='count_new',
                          body=json.dumps(data_list))
    print('放队列 {}'.format(data_list))
    data_list.clear()


if __name__ == '__main__':
    run()