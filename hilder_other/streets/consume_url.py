import json
import pika
import gevent
import requests
import yaml
from gevent import monkey

monkey.patch_all()

setting = yaml.load(open('config.yaml'))

connection_result = pika.BlockingConnection(
    pika.ConnectionParameters(host=setting['jquerycitys']['rabbitmq']['host'],
                              port=setting['jquerycitys']['rabbitmq']['port']))
channel_result = connection_result.channel()


def async_message(_url):
    try:
        connection_result.process_data_events()
        result = requests.get(_url, timeout=5)
        connection_result.process_data_events()
    except Exception as e:
        return

    #提取json中的数据,将一个请求的结果作为一个列表存入到结果队列中
    result_list = list(result.json().values())

    channel_result.queue_declare(queue='other_result_json')
    channel_result.basic_publish(exchange='',
                                 routing_key='other_result_json',
                                 body=json.dumps(result_list))

def callback(ch, method, properties, body):
    jobs = [gevent.spawn(async_message, _url) for _url in json.loads(body.decode())]
    gevent.wait(jobs)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_all_url():
    channel = connection_result.channel()
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,
                          queue='other_city_url',
                          )
    channel.start_consuming()
