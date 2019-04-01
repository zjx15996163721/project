from pymongo import MongoClient
import pika

m = MongoClient(host='192.168.0.235',
                port=27777,
                username='goojia',
                password='goojia7102')

comm_collection = m['friends']['xiaozijia_comm']

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673))
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_price')


def get_price():
    for i in comm_collection.find(no_cursor_timeout=True):
        # ConstructionPhaseId 用于搜索小区均价
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_price',
                              body=i['ConstructionPhaseId'])


if __name__ == '__main__':
    get_price()
