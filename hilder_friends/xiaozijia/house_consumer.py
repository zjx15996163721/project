"""
    消费xiaozijia_house_detail队列，请求，入楼栋库xiaozijia_detail_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
import requests
import pika
from lib.proxy_iterator import Proxies

log = LogHandler(__name__)

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')

collection = m.connect['friends']['xiaozijia_house_detail_10_8']
p = Proxies()
proxies = next(p)


def change():
    pass


class HouseDetail:
    def message(self, info):
        headers = {'Cookie': 'ASP.NET_SessionId=ljclydfzzajvvc4zalmvppcz;',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

        detail_url = 'http://www.xiaozijia.cn/HouseInfo/' + info
        print('url={}'.format(detail_url))
        try:
            response = requests.get(detail_url, headers=headers, proxies=proxies, timeout=10)
            print(response.json())
            html_json = response.json()
            print(html_json)
            collection.insert_one(html_json)
        except Exception as e:
            print(e)
            log.error('url={}'.format(detail_url))

    def callback(self, ch, method, properties, body):
        self.message(body.decode())
        print('-----------------------------------')
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_all_url(self):
        # connect_result = pika.BlockingConnection(
        #     pika.ConnectionParameters(host='localhost', port=5673))
        connect_result = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5673))
        channel = connect_result.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='xzj_house_id',
                              )
        channel.start_consuming()
