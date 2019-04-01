# coding=utf-8
"""
根据城市的经纬度获取高德所有的poi
城市经纬度数据库地址
host:192.168.0.136
port:27017
db:fangjia_base
collection:city_bounds_box

把对角点的经纬度+类型放入 队列 amap_all_url
一共900w+对对角点
"""
from lib.mongo import Mongo
from amap_reconfiguration.amap_exception import AmapException
from amap_reconfiguration.api_builder import ApiKey, api_key_list
import pika
import json

m = Mongo('192.168.0.136')
collection = m.connect['fangjia_base']['city_bounds_box']

API_KEY_BUILDER = ApiKey()
DAILY_COUNT_ACCORDING_KEYS = len(api_key_list) * 300000


def all_url(a_type, rabbit):
    """
    把类型和经纬度放入amap_all_url队列
    :param a_type:
    :param rabbit:
    :return:
    """
    url_list = []
    for info in collection.find({'city': {'$nin': ['中国']}}):
        square_list = info['bound_gd']
        square_ = str(square_list[0]) + ',' + str(square_list[1]) + ';' + str(square_list[2]) + ',' + str(
            square_list[3])
        url = 'http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + a_type + '&output=JSON&key=' + \
              next(API_KEY_BUILDER) + '&offset=50'
        url_list.append(url)
        if len(url_list) == 100:
            print('放入队列')
            rabbit.basic_publish(exchange='',
                                 routing_key='amap_all_url',
                                 body=json.dumps(url_list),
                                 )
            url_list.clear()


def check_power(type_list):
    type_count = len(type_list)
    print(DAILY_COUNT_ACCORDING_KEYS)
    if type_count * 9409786 > DAILY_COUNT_ACCORDING_KEYS:
        raise AmapException


def put_all_url_into_queue():
    type_list = ['010000', ]
    check_power(type_list)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.193', port=5673))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_url')
    for a_type in type_list:
        all_url(a_type, rabbit)


if __name__ == '__main__':
    put_all_url_into_queue()
