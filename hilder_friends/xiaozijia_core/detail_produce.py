import itertools
import pika
from lib.mongo import Mongo
import json

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
collection = m.connect['friends']['xiaozijia_house']

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.190', 5673))
channel = connection.channel()


def put_detail_in_rabbit():
    url_list = []
    count = 1
    for i in collection.find(no_cursor_timeout=True):
        if count % 500 == 0:
            channel.queue_declare(queue='xiaozijia_detail')
            channel.basic_publish(exchange='',
                                  routing_key='xiaozijia_detail',
                                  body=json.dumps(url_list))
            url_list.clear()
            count = count + 1
        else:
            url_list.append({
                'Id': i['Id']
            })
            count = count + 1
