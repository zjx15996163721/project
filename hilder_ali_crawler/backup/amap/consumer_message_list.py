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

r_result = Rabbit(host=host, port=port)
r_page = Rabbit(host=host, port=port)


def requests_a(result):
    print('-----------------{}'.format(result.text))
    if 'DAILY_QUERY_OVER_LIMIT' in result.text:
        sys.exit()
    try:
        status = result.json()['status']
    except Exception as e:
        print(e)
        print(result)
        return
    if status is '1':
        count = int(result.json()['count'])
        if count != 0:
            if count < 50:
                print('count < 50')

                connection_result = r_result.connection
                channel = connection_result.channel()
                channel.queue_declare(queue='amap_result_json')
                channel.basic_publish(exchange='', routing_key='amap_result_json', body=json.dumps(result.json()))
                channel.close()
                print(result.json())

                # connection_result.close()
            else:
                print('count > 50')

                # connection_page = r_page.connection
                # channel = connection_page.channel()
                # channel.queue_declare(queue='amap_page_url')
                # for i in range(1, int(count / 50 + 0.5)):
                #     channel.basic_publish(exchange='',
                #                           routing_key='amap_page_url',
                #                           body='http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + type_ + '&output=JSON&offset=50' + '&page=' + str(
                #                               i + 1), )
                #     print('分页 的url放入')
                # channel.close()

                # connection_page.close()
        else:
            print('count = 0')
            return
    else:
        return



@trip.coroutine
def asyn_message(body,api_key):
    body = body.decode('utf8')
    url_list = []
    for i in json.loads(body):
        s, t = i['square_list'], i['type']
        square_ = str(s[0]) + ',' + str(s[1]) + ';' + str(s[2]) + ',' + str(s[3])
        url_list.append('http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + t + '&output=JSON&key=' + \
          api_key + '&offset=50')
    r = yield [trip.get(url) for url in url_list]
    for result in r:
        requests_a(result)


def callback(ch, method, properties, body):
    """
    {'type': '010000', 'square_list': [73.010906, 44.471043, 73.510906, 43.971043]}
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    api_key = method.consumer_tag
    trip.run(partial(asyn_message,body,api_key))
    # ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_all_url(api_key):
    rabbit = Rabbit(host=host, port=port)
    connection_result = rabbit.connection
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection_result.channel()
    # channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='amap_url_list', consumer_tag=api_key)
    channel.start_consuming()
