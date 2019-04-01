"""
    消费xiaozijia_house_detail队列，请求，入楼栋库xiaozijia_detail_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
import requests
import json
import pika
import itertools

log = LogHandler(__name__)

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
# m = Mongo(host='localhost', port=27017)


user_collection = m.connect['friends']['xiaozijia_user']
cookie_iter = itertools.cycle([_['cookie'] for _ in user_collection.find(no_cursor_timeout=True)])
collection = m.connect['friends']['xiaozijia_house_detail']

proxies = {
    'http': 'localhost:8787',
    'https': 'localhost:8787'
}

def change():
    pass

class HouseDetail:
    def message(self, info):
        headers = {
            'Cookie': next(cookie_iter),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        detail_url = 'http://www.xiaozijia.cn/HouseInfo/' + str(info['Id'])
        try:
            response = requests.get(detail_url, headers=headers, proxies=proxies, timeout=10)
            if '禁止访问' in response.content.decode('gbk'):
                # todo 切换账号
                change()
            html_json = response.json()
            print(html_json)
            collection.insert_one(html_json)
        except Exception as e:
            print(e)
            log.error('url={}'.format(detail_url))

    def callback(self, ch, method, properties, body):
        for info in json.loads(body.decode()):
            self.message(info)
        print('-----------------------------------')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_all_url(self):
        # connect_result = pika.BlockingConnection(
        #     pika.ConnectionParameters(host='localhost', port=5673))
        connect_result = pika.BlockingConnection(
            pika.ConnectionParameters(host='114.80.150.195', port=5673))
        channel = connect_result.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='xiaozijia_detail',
                              )
        channel.start_consuming()
