"""
爬取顺序：城市-区域-街道-菜系
start:1
"""
import yaml
import json
import random
import pika
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
city_queue = setting['dianping']['rabbit']['queue']['city_queue']
channel.queue_declare(queue=city_queue)

# mongo
m = Mongo(setting['dianping']['mongo']['host'], setting['dianping']['mongo']['port'])
coll = m.connect[setting['dianping']['mongo']['db']][setting['dianping']['mongo']['find_coll']]

kind_list = {
    # '美食': 'ch10',
    # '休闲娱乐': 'ch30',
    # '丽人': 'ch50',
    # '周边游': 'ch35',
    # '运动健身': 'ch45',
    # '购物': 'ch20',
    # '学习培训': 'ch75',
    # '生活服务': 'ch80',
    # '医疗健康': 'ch85',
    '爱车': 'ch65',
    # '宠物': 'ch95',

    # 四个类型不一样的
    # '家装': 'ch90',
    # '亲子': 'ch70',
    # '酒店': 'hotel/',
    # '结婚': 'ch55',
}


def start_consume():
    for kind_code in kind_list:
        for city in coll.find():
            city_name = city['city']
            pinyin = city['pinyin']
            data = {
                'city_name': city_name,
                'pinyin': pinyin,
                'kind_code': kind_list[kind_code],
            }
            channel.basic_publish(exchange='',
                                  routing_key=city_queue,
                                  body=json.dumps(data),
                                  properties=pika.BasicProperties(
                                      delivery_mode=2))
            print('+' * random.randint(1, 50))


if __name__ == '__main__':
    start_consume()
