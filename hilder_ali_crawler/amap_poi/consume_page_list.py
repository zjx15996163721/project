import pika
import json
import yaml
from lib.log import LogHandler
import requests
import gevent
from gevent import monkey

monkey.patch_all()

setting = yaml.load(open('config_amap.yaml'))
rabbit_setting = setting['amap']['rabbitmq']
log = LogHandler(__name__)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_setting['host'], port=rabbit_setting['port'],heartbeat=0))
rabbit = connection.channel()
rabbit.queue_declare(queue='amap_page_url')


def async_message(_url):
    try:
        # connection.process_data_events()
        result = requests.get(_url, timeout=5)
        # connection.process_data_events()
    except Exception as e:
        log.error('request error,url={}'.format(_url))
        return
    status = result.json()['status']
    if status is '1':
        count = int(result.json()['count'])
        if count != 0:
            rabbit.queue_declare(queue='amap_result_json')
            rabbit.basic_publish(exchange='',
                                 routing_key='amap_result_json',
                                 body=json.dumps(result.json())
                                 )


def callback(ch, method, properties, body):
    print('消费分页url')
    jobs = [gevent.spawn(async_message, _url) for _url in json.loads(body.decode())]
    gevent.wait(jobs)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_page_url():
    rabbit.basic_qos(prefetch_count=10)
    rabbit.basic_consume(callback,
                         queue='amap_page_url',
                         )
    rabbit.start_consuming()
