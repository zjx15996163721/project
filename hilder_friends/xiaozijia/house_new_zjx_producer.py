from lib.log import LogHandler
from pymongo import MongoClient
import requests
import pika
import json
from lib.proxy_iterator import Proxies
log = LogHandler(__name__)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')

xiaozijia_build_collection = m['friends']['xiaozijia_build']
xiaozijia_house_2018_10_8_collection = m['friends']['xiaozijia_house_2018_10_8']
p = Proxies()
proxies = p.get_one(proxies_number=6)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()


class Producer(object):

    def __init__(self, cookie):
        self.headers = {
            'Host': 'www.xiaozijia.cn',
            'Referer': 'http://www.xiaozijia.cn/Evaluation/Evaluation',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            'Cookie': cookie
        }

    def get_house_url(self, IdSub):
        url = 'http://www.xiaozijia.cn/HousesForJson/{}/1'.format(IdSub)
        print(url)
        r = requests.get(url=url, headers=self.headers, proxies=proxies)
        print(r.status_code)
        print(r.text)
        if r.status_code == 200:
            data = {
                'data': r.json()
            }
            xiaozijia_house_2018_10_8_collection.insert(data)
            log.info('插入一条数据 {}'.format(data))
            try:
                self.insert_queue(r.json())
            except Exception as e:
                log.error('数据为空 e={}'.format(e))
        else:
            log.error('请求失败, url={}'.format(url))

    def insert_queue(self, data):
        first_data = data[0]
        data_Id = first_data['Id']
        IdSub = first_data['IdSub']
        url = 'http://www.xiaozijia.cn/HouseInfo/{}T{}'.format(str(data_Id), str(IdSub))
        channel.queue_declare(queue='xiaozijia_detail_url')
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_detail_url',
                              body=json.dumps(url))
        log.info('一条url放队列 url={}'.format(url))

    def callback(self, ch, method, properties, body):
        IdSub = json.loads(body.decode())
        self.get_house_url(IdSub)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        channel.queue_declare(queue='xiaozijia_IdSub')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='xiaozijia_IdSub')
        channel.start_consuming()


if __name__ == '__main__':
    p = Producer('传个cookie')
    p.start_consuming()
