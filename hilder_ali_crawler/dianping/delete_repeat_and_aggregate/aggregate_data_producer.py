"""
聚合
"""
from pymongo import MongoClient
import yaml
import pika
import json
from multiprocessing import  Process
setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
dianping_all_type_lat_collection = db[setting['mongo']['shop_lat_collection']]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port'], heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='dianping_no_lat', durable=True)


def aggregate():
    count = 0
    for i in dianping_all_type_collection.find(no_cursor_timeout=True):
        count += 1
        data = dianping_all_type_lat_collection.find_one({'id': i['id']})
        if data is None:
            channel.basic_publish(exchange='',
                                  routing_key='dianping_no_lat',
                                  body=json.dumps(i['id']),
                                  properties=pika.BasicProperties(delivery_mode=2,))  # 设置消息持久化
            print('这条数据没有查到经纬度，ID放队列 id={}'.format(i['id']))
            print('到第{}个'.format(count))
        else:
            dianping_all_type_collection.update_one({'id': i['id']}, {'$set': {'lat': data['lat'], 'lng': data['lng'], 'info': data['info']}})
            print('这条数据查到经纬度，更新这条数据，添加经纬度')
            print('到第{}个'.format(count))


# def aggregate_test(num):
#     count = 0
#     for i in dianping_all_type_collection.find(skip=5000000*num, limit=5000000, no_cursor_timeout=True):
#         count += 1
#         data = dianping_all_type_lat_collection.find_one({'id': i['id']})
#         if data is None:
#             channel.basic_publish(exchange='',
#                                   routing_key='dianping_no_lat',
#                                   body=json.dumps(i['id']))
#             print('这条数据没有查到经纬度，ID放队列 id={}'.format(i['id']))
#             print('到第{}个'.format(count))
#         else:
#             dianping_all_type_collection.update_one({'id': i['id']}, {
#                 '$set': {'lat': data['lat'], 'lng': data['lng'], 'info': data['info']}})
#             print('这条数据查到经纬度，更新这条数据，添加经纬度')
#             print('到第{}个'.format(count))


if __name__ == '__main__':
    aggregate()
    # aggregate_test()
    # for i in range(0, 9):
    #     Process(target=aggregate_test(i)).start()
