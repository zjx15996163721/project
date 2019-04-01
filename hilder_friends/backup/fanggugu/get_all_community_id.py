"""
从235，fgg，fanggugu_price库中查小区id,城市名字
放入队列235，fgg_community_id
"""
import pymongo
import pika
import json


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=5673))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


coll_com = connect_mongodb('192.168.0.235', 27017, 'fgg', 'fanggugu_price')
channel = connect_rabbit('192.168.0.235', 'fgg_community_id')


def produce():
    for i in coll_com.find():
        ResidentialAreaID = i['ResidentialAreaID']
        city_name = i['city_name']
        data = {
            'ResidentialAreaID': ResidentialAreaID,
            'city_name': city_name,
        }
        print(data)
        channel.basic_publish(exchange='',
                              routing_key='fgg_community_id',
                              body=json.dumps(data),
                              )
