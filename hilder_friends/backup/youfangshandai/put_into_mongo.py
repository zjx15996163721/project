import pika
import pymongo
import json
import random

connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.190', 5673))
channel = connection.channel()
coll = pymongo.MongoClient('192.168.0.235', 27017)['friends'].get_collection('yfsd_April')
channel.queue_declare(queue='yfsd_house')
count = 0


def callback(ch, method, properties, body):
    body = json.loads(body.decode())
    resultData = body.get('resultData')
    city = body.get('city')
    for i in resultData:
        i['city'] = city
    print(resultData)
    coll.insert_many(resultData)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consume():
    # 类似权重，按能力分发，如果有一个消息，就不在给你发
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='yfsd_house', )
    channel.start_consuming()


if __name__ == "__main__":
    start_consume()
