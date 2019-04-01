"""
id sub 不能重复
如果IdSub不再redis存在，把Id放入消息队列
IdSub 表示一个楼栋
"""

import redis
from pymongo import MongoClient
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673))
channel = connection.channel()
channel.queue_declare(queue='xzj_house_id')
r = redis.Redis(host="127.0.0.1", port=6379, db=0)

m = MongoClient(host='114.80.150.196', port=27777)
collection = m['friends']['xiaozijia_house']

count = 0
for i in collection.find(no_cursor_timeout=True):
    # 0 存在 1 不存在
    count = count + 1
    print(count)
    result = r.sadd('IdSub_', i['IdSub'])
    if result == 0:
        # put in mq
        channel.basic_publish(exchange='',
                              routing_key='xzj_house_id',
                              body=str(i['Id']))
