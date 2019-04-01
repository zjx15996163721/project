import requests
import pymongo
import hashlib
from retry import retry
import pika


def get_collection_object(host, port, db_name, collection_name):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]
    return collection


m = get_collection_object('192.168.0.61', 27017, 'buildings', 'house_image_demo2')
# credentials = pika.PlainCredentials('guest1', 'guest')
# connection = pika.BlockingConnection(pika.ConnectionParameters(
#     '192.168.10.127', 5673, '/', credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.190',5673))
channel = connection.channel()
channel.queue_declare(queue='img_url_test')

for i in m.find():
    image_list = i['image_list']
    for i in image_list:
        img = i['img']
        channel.basic_publish(exchange='',
                              routing_key='img_url_test',
                              body=img
                              )
