"""
poi 详情 官方详情
"""
import requests
import pymongo
from multiprocessing import Process
import pika

client = pymongo.MongoClient('192.168.0.235', 27017)
db = client['amap']
detail_coll = db.get_collection('poi_detail_official')

count = 0


def put_key_into_rabbit():
    # 把所有的key放入rabbit
    client = pymongo.MongoClient('192.168.0.235', 27017)
    db = client['amap']
    poi_coll = db.get_collection('poi_new')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.235', ))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_poi_id')
    for poi in poi_coll.find(no_cursor_timeout=True):
        poi_id = poi['id']
        rabbit.basic_publish(exchange='',
                             routing_key='amap_all_poi_id',
                             body=poi_id, )


def callback(ch, method, properties, body):
    global count
    count += 1
    if count < 300000:
        body = body.decode()
        key = method.consumer_tag

        url = 'http://restapi.amap.com/v3/place/detail?id=' + body + "&key=" + key + "&output=json"
        result = requests.get(url).json()
        # print(result)
        if result['status'] is '1':
            try:
                detail_coll.insert({'_id': body, 'pois': result['pois']})
            except pymongo.errors.DuplicateKeyError as e:
                print('插入的key相同')
        else:
            print('status is not 1: ', result)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print('超过限制')


def consume_poi_id(key):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.235', ))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_poi_id')
    rabbit.basic_qos(prefetch_count=1)
    rabbit.basic_consume(callback,
                         queue='amap_all_poi_id',
                         consumer_tag=key,
                         )
    rabbit.start_consuming()


if __name__ == '__main__':
    put_key_into_rabbit()
    # keys = ['5291708fd06289fce26ac6777d8f507a',
    #         '2717071312b735cfd5fdc65302a88cd1',
    #         'ab69aedc73d6ea693c44a5d529d3fd29',
    #         'debecb80b8ab7eaf816fafd20f689b5d',
    #         'fa9ed434ecaca6ced1c598c3ac531bff',
    #         '3b4abe69b9011a9511c5d09e0c5ecbd0',
    #         'ebd199270a493da94bae0c06ac868177',
    #         '44c2db2a48d1ab47989688c7c37a2dd8',
    #         '01ec31886825b59530a6fa7f2646bd12',
    #         'b8987f1bab289cf7e413098e624ea9e9',
    #         '2af0b8533415a612b98d59bb93d664b9',
    #         '0246c57bbcf24aa246c207b3c99dfe41',
    #         '042328b3f0fa5daf426802d379521d87',
    #         '055d4f1b5b64a2bce18f4fe1f15c2639',
    #         'd5484f5170502405d88bbaffe1b496f0',
    #         'e74ccc4258079d2200199695110cceb1',
    #         'f58629fc799fbc8537ca85046c6d44a5',
    #         '291073f17ee0b963ccb1927ed92bf265',
    #         '2a1fb75990f2b39f6221e50892dd3988',
    #         '4ccfe3c898a9489884bd2bcb1ef6dcde', ]
    # for i in keys:
    #     p = Process(target=consume_poi_id, args=(i,))
    #     p.start()
