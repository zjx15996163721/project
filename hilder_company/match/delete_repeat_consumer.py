"""
消费线上的队列  去重
"""
from pymongo import MongoClient
import redis
import pika
import json
from multiprocessing import Process
r = redis.Redis(host='localhost', port='6379')
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
company_crawler_collection = m['company']['company_crawler']

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='company_repeat')


def delete(data):
    company_name = data['company_name']
    city = data['city']
    address = data['address']
    company_crawler_collection.delete_one({'company_name': company_name, 'city': city, 'address': address})
    print("删除一条数据 company_name={}".format(company_name))


def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    delete(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def run():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='company_repeat')
    channel.start_consuming()


if __name__ == '__main__':
    for i in range(10):
        Process(target=run).start()
