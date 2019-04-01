import json
import pika
import gevent
import requests
import yaml
from lib.log import LogHandler
import math
from gevent import monkey

monkey.patch_all()
log = LogHandler(__name__)
setting = yaml.load(open('config_amap.yaml'))

connection_result = pika.BlockingConnection(
    pika.ConnectionParameters(host=setting['amap']['rabbitmq']['host'],
                              port=setting['amap']['rabbitmq']['port'],
                              heartbeat=0)
                            )
channel_result = connection_result.channel()
channel_page = connection_result.channel()
channel_result.queue_declare(queue='amap_all_url')
# channel_page.queue_declare(queue='amap_page_url')


def async_message(_url):
    try:
        # connection_result.process_data_events()
        result = requests.get(_url, timeout=5)
        # connection_result.process_data_events()
    except Exception as e:
        log.error('request error,url={}'.format(_url))
        return

    status = result.json()['status']

    if status is '1':
        count = int(result.json()['count'])
        if count != 0:
            channel_result.queue_declare(queue='amap_result_json')
            channel_result.basic_publish(exchange='',
                                         routing_key='amap_result_json',
                                         body=json.dumps(result.json()))
            if count > 50:
                print('count > 50')
                channel_page.queue_declare(queue='amap_page_url')
                page_url_list = []
                for i in range(2, int(math.ceil(count / 50) + 1)):
                    page_url_list.append(result.url.replace('page=1', 'page={}'.format(str(i))))
                channel_page.basic_publish(exchange='',
                                           routing_key='amap_page_url',
                                           body=json.dumps(page_url_list))
                print(page_url_list)
                page_url_list.clear()
                print('分页 的url放入从第二页开始放入到amap_all_url队列中')
    else:
        log.error('url={},result={}'.format(_url, result.text))


def callback(ch, method, properties, body):
    jobs = [gevent.spawn(async_message, _url) for _url in json.loads(body.decode())]
    gevent.wait(jobs)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_all_url():
    channel = connection_result.channel()
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,
                          queue='amap_all_url',
                          )
    channel.start_consuming()
