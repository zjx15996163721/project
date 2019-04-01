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
import pika
import json

m = Mongo('192.168.0.136')
collection = m.connect['fangjia_base']['city_bounds_box']


def all_url(a_type, rabbit):
    """
    把类型和经纬度放入amap_all_url队列
    :param a_type:
    :param rabbit:
    :return:
    """

    for info in collection.find({'city': {'$nin': ['中国']}}):
        square_list = info['bound_gd']
        body = json.dumps({'square_list': square_list, 'type': a_type})
        print(body)
        rabbit.basic_publish(exchange='',
                             routing_key='amap_all_url',
                             body=body,
                             )


def put_all_url_into_queue():
    # type_list = ['060000', '120000']
    # type_list = ['120100']
    # type_list = ['120300']
    # type_list = ['060100']
    # type_list = ['120200']
    type_list = ['060101']
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='192.168.0.190', port=5673, heartbeat=0, socket_timeout=6000))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_url')
    for a_type in type_list:
        all_url(a_type, rabbit)


if __name__ == '__main__':
    put_all_url_into_queue()
