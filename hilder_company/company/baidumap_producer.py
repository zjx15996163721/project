from pymongo import MongoClient
import yaml
import pika
import json
clent = MongoClient(
    host='192.168.0.136',
    port=27017,
)
mongo_connection = clent['fangjia']['seaweed']

pika_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1',
    port=5673,
    heartbeat=0
))

channel = pika_connection.channel()
channel.queue_declare(queue='baidu_producer',durable=True)

def baiduproducer():
    results = mongo_connection.find({'cat':"office",'status':0})
    small_list = []
    for result in results[72118:82017]:
        city = result['city']
        region = result['region']
        address = result['address']
        if address is not None:
            address_string = city + region + address
        else:
            address_string = city + region
            print(result)
        small_dict = {}
        small_dict['city'] = city
        small_dict['region'] = region
        small_dict['search_word'] = address_string
        small_dict['match_word'] = address
        small_list.append(small_dict)
        if len(small_list) == 9:
            channel.basic_publish(
                exchange='',
                routing_key='baidu_producer',
                body=json.dumps(small_list),
                properties=pika.BasicProperties(delivery_mode=2, )
            )
            small_list.clear()
            print('放入一个列表')


if __name__ == '__main__':
    baiduproducer()


