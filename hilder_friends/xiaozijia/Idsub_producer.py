from pymongo import MongoClient
from lib.log import LogHandler
import pika
import json
log = LogHandler(__name__)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
xiaozijia_build_collection = m['friends']['xiaozijia_build']

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_IdSub')


def producer():
    for i in xiaozijia_build_collection.find(no_cursor_timeout=True):
        IdSub = i['IdSub']
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_IdSub',
                              body=json.dumps(IdSub))
        log.info('一条IdSub放队列 IdSub={}'.format(IdSub))


if __name__ == '__main__':
    producer()