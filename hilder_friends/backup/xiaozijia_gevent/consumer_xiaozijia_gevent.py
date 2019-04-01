import gevent
import requests
import json
from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from xiaozijia_gevent.user_headers import get_headers
from xiaozijia_gevent.user_list import user_list
from multiprocessing import Process
from gevent import monkey
import random

log = LogHandler(__name__)
m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
coll_detail = m.connect['friends']['xiaozijia_detail']

r = Rabbit('localhost', 5673)
channel = r.get_channel()
gevent.monkey.patch_all()
headers = ''


def detail_message(info):
    global headers
    data = json.loads(info)
    username = random.choice(user_list)
    headers = get_headers(username)
    id = data['Id']
    ConstructionName = data['ConstructionName']
    try:
        detail_url = 'http://www.xiaozijia.cn/HouseInfo/' + str(id)
        result = requests.get(detail_url, headers=headers, timeout=10)
        print(result.text, detail_url)
    except Exception as e:
        headers = get_headers(username)
        log.info('request error,id={}'.format(id))
        return
    html = result.json()
    html['ConstructionName'] = ConstructionName
    coll_detail.insert_one(html)


def data_const(ch, method, properties, body):
    list_info = json.loads(body.decode())
    jobs = [gevent.spawn(detail_message, info) for info in list_info]
    gevent.joinall(jobs)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=data_const, queue='xiaozijia_gevent')
    channel.start_consuming()


if __name__ == '__main__':
    # for i in range(50):
    from threading import Thread
    Process(target=consume_queue).start()
