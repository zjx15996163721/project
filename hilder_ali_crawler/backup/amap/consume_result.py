# coding=utf-8
import pika
import pymongo
import json
import yaml

client = pymongo.MongoClient('192.168.0.235', 27017)
db = client['amap']
coll = db.get_collection('poi_new_2018_5')
setting = yaml.load(open('config.yaml'))
host = setting['amap']['rabbitmq']['host']
port = setting['amap']['rabbitmq']['port']

def callback(ch, method, properties, body):
    print(body.decode())
    json_result = json.loads(body.decode())
    pois = json_result.get('pois')
    if pois:
        # print(pois)
        coll.insert_many(pois)
    print('存储入库完毕')
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume(rabbit_):
    rabbit_.basic_qos(prefetch_count=1)
    rabbit_.basic_consume(callback,
                          queue='amap_result_json',
                          )
    rabbit_.start_consuming()


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    rabbit = connection.channel()
    consume(rabbit)
