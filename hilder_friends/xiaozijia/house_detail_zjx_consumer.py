from lib.log import LogHandler
from lib.mongo import Mongo
import requests
import pika
import json
from lib.proxy_iterator import Proxies
log = LogHandler(__name__)

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')

xiaozijia_build_collection = m.connect['friends']['xiaozijia_build']
xiaozijia_house_detail_2018_10_8_collection = m.connect['friends']['xiaozijia_house_detail_2018_10_8']
p = Proxies()
proxies = p.get_one(proxies_number=5)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_detail_url')


class Consumer(object):

    def __init__(self, cookie):
        self.headers = {
            'Host': 'www.xiaozijia.cn',
            'Referer': 'http://www.xiaozijia.cn/Evaluation/Evaluation',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie': cookie
        }

    def callback(self, ch, method, properties, body):
        url = json.loads(body.decode())
        try:
            r = requests.get(url=url, headers=self.headers, proxies=proxies)
            data = r.json()
            xiaozijia_house_detail_2018_10_8_collection.insert_one(data)
            log.info('插入一条数据 data={}'.format(data))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            log.error('请求失败 url={}， e={}'.format(url, e))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

    def start_consuming(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='xiaozijia_detail_url')
        channel.start_consuming()


if __name__ == '__main__':
    c = Consumer('传个cookie')
    c.start_consuming()