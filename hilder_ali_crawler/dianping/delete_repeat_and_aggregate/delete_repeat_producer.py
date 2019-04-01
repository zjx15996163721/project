"""
去重
"""
from pymongo import MongoClient
import redis
import yaml
import pika
import json
setting = yaml.load(open('config_dianping.yaml'))
r = redis.Redis(host=setting['redis']['host'], port=setting['redis']['port'])
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
# dianping_all_type_lat_collection = db[setting['mongo']['shop_lat_collection']]
# 第二张表去重时，更换表名和redis的key值, 队列名称
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port'], heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='dianping_shop_detail_repeat_id_list')


def run():
    count = 0
    for i in dianping_all_type_collection.find(no_cursor_timeout=True):
        count += 1
        flag = r.sadd('dianping_shop_detail_repeat_id_list', i['id'])
        if flag == 1:
            print('ID不存在{} 添加到redis'.format(i['id']))
            print(count)
        elif flag == 0:
            channel.basic_publish(exchange='',
                                  routing_key='dianping_shop_detail_repeat_id_list',
                                  body=json.dumps(i['id']))
            print('ID已经存在，放队列 {}'.format(i['id']))
            print(count)


if __name__ == '__main__':
    run()

