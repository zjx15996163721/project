# coding=utf-8
"""
消费amap_all_url队列，请求
如果数据量小于50条，直接放入amap_result_json队列
大于50条，则放入amap_page_url队列

"""
import json
from lib.rabbitmq import Rabbit
from functools import partial
import sys
import yaml
import pika
import trip

setting = yaml.load(open('config.yaml'))
host = setting['amap']['rabbitmq']['host']
port = setting['amap']['rabbitmq']['port']

message_list = []

r_result = Rabbit(host=host, port=port)
connection_result = r_result.connection

channel = connection_result.channel()

def callback(ch, method, properties, body):
    """
    {'type': '010000', 'square_list': [73.010906, 44.471043, 73.510906, 43.971043]}
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    body = json.loads(body.decode('utf8'))
    if len(message_list) < 20:
        api_key = method.consumer_tag
        message_list.append(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # put_in_new_mq()
        channel_ = connection_result.channel()
        channel_.queue_declare(queue='amap_url_list')
        channel_.basic_publish(exchange='', routing_key='amap_url_list', body=json.dumps(message_list))
        channel_.close()

        message_list.clear()
        message_list.append(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)



def consume_all_url(api_key):
    rabbit = Rabbit(host=host, port=port)
    connection_result = rabbit.connection
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection_result.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='amap_all_url', consumer_tag=api_key)
    channel.start_consuming()
