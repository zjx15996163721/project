"""
mongo地址存放136/fangjia_crawl/xiaozijia_price
"""

import requests
from pymongo import MongoClient
import pika
from lib.proxy_iterator import Proxies
from lib.log import LogHandler

log = LogHandler(__name__)

p = Proxies()

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')

comm_collection = m['fangjia_crawl']['xiaozijia_price_1']

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_price')


class Price:
    def __init__(self):
        self.proxies = next(p)
        self.url = 'http://www.xiaozijia.cn/Chart/GetConPRT/'
        self.headers = {'Cookie': 'ASP.NET_SessionId=og4urfucgr4mla2ipov1mdkz;',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

    def start_consume(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='xiaozijia_price',
                              )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        comm_id = body.decode()
        print(comm_id)
        r = requests.get(url=self.url + comm_id, headers=self.headers, proxies=self.proxies)
        print(r.text)
        try:
            if 'An error condition occurred' in r.text:
                log.error(comm_id)
                print('切换代理')
                self.proxies = next(p)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print('准备入入库')
                comm_collection.insert({'_id': comm_id, 'info': r.json()})

                ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            log.error(comm_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
