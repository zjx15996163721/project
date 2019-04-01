"""
根据城市的adcode获取高德所有的poi,
利用城市和分类来拼接url地址
"""
from amap_poi.city_category import city_code, type_code
import pika
import json
import yaml
import itertools
from amap_poi.api_key_list import api_key_list

keys = itertools.cycle(api_key_list)

setting = yaml.load(open('config_amap.yaml'))


def all_url(rabbit):
    """
    所有城市，分类
    :param rabbit:
    :return:
    """
    url_list = []
    for adcode in city_code:
        for cate_code in type_code:
            url = 'http://restapi.amap.com/v3/place/text?types={}&city={}&output=JSON&key={}&offset=50&page=1'.format(
                cate_code, adcode, next(keys))
            print(url)
            url_list.append(url)
            if len(url_list) == 100:
                print('放入队列')
                rabbit.basic_publish(exchange='',
                                     routing_key='amap_all_url',
                                     body=json.dumps(url_list))
                url_list.clear()


def put_all_url_into_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['amap']['rabbitmq']['host'],
                                                                   port=setting['amap']['rabbitmq']['port']))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_url')
    all_url(rabbit)
    connection.close()
