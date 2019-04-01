"""
去重
"""
from pymongo import MongoClient
import redis
import yaml
import pika
import json
from multiprocessing import Process
setting = yaml.load(open('config_dianping.yaml'))
r = redis.Redis(host=setting['redis']['host'], port=setting['redis']['port'])
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
dianping_all_type_lat_collection = db[setting['mongo']['shop_lat_collection']]
# 第二张表去重时，更换表名和redis的key值, 队列名称
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='dianping_shop_lat_repeat_id_list')
connection.process_data_events()


def delete(shop_id):
    dianping_all_type_lat_collection.delete_one({'id': shop_id})
    print("删除一条数据 ID={}".format(shop_id))


def callback(ch, method, properties, body):
    shop_id = json.loads(body.decode())
    delete(shop_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def run():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='dianping_shop_lat_repeat_id_list')
    channel.start_consuming()


if __name__ == '__main__':
    for i in range(10):
        Process(target=run).start()
