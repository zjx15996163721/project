"""
根据经纬度，分类获取高德所有的poi,主要是从数据库（数据已经存在）中读取经纬度，然后拼接url,将其放入到url队列中

"""
from pymongo import MongoClient
import pika
import json
import yaml
import itertools
from amap_poi.api_key_list import api_key_list

keys = itertools.cycle(api_key_list)
# 这四类主要是内容比较多，即使采用adcode,内容还是很多，所以这四类采用经纬度进行分割，分为一小块
type_code = ['050000', '060000', '170000', '190000']

# 链接远程数据库，获取经纬度
client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102')
db = client['fangjia_base']
collection = db['city_bounds_box']

setting = yaml.load(open('config_amap.yaml'))


def all_url(rabbit):
    """
    所有城市，分类
    :param rabbit:
    :return:
    """
    url_list = []
    for i in collection.find({}):
        lat_list = i['bound_gd']
        # print(lat_list)
        lat_one = str(lat_list[0]) + ',' + str(lat_list[1])
        lat_two = str(lat_list[2]) + ',' + str(lat_list[3])
        for cate_code in type_code:
            url = 'https://restapi.amap.com/v3/place/polygon?polygon={}|{}&types={}&output=json&key={}&offset=50&page=1'.format(
                lat_one, lat_two, cate_code, next(keys))
            url_list.append(url)
            print(url)
            if len(url_list) == 100:
                print('放入队列')
                rabbit.basic_publish(exchange='',
                                     routing_key='amap_all_url',
                                     body=json.dumps(url_list), )
                url_list.clear()


def put_lat_url_into_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['amap']['rabbitmq']['host'],
                                                                   port=setting['amap']['rabbitmq']['port']))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_url')
    all_url(rabbit)
    connection.close()
