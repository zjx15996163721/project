"""
    消费xiaozijia_house_detail队列，请求，入楼栋库xiaozijia_detail_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
import requests
import json
import gevent
import pika
import itertools
import time

log = LogHandler(__name__)

# m = Mongo(host='localhost', port=27017)
m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
user_collection = m.connect['friends']['xiaozijia_user']

proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
    "host": "http-proxy-sg2.dobel.cn",
    "port": "9180",
    "account": 'FANGJIAHTT7',
    "password": "HGhyd7BF",
}
proxies = {"https": proxy,
           "http": proxy}


class HouseDetail:
    def asyn_message(self, info, cookie_iter):
        headers = {
            'Cookie': next(cookie_iter),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        detail_url = 'http://www.xiaozijia.cn/HouseInfo/' + str(info['Id'])
        try:
            response = requests.get(detail_url, headers=headers, proxies=proxies, timeout=10)
            html_json = response.json()
            print(html_json)
            return html_json
        except Exception as e:
            print(e)
            log.error('url={}'.format(detail_url))

    # def split_body(self, body):
    #     id_list = json.loads(body.decode())
    #     return [id_list[0:33], id_list[33:66], id_list[66:]]

    def callback(self, ch, method, properties, body):
        # new_list = self.split_body(body)
        # collection = m.connect['friends']['xiaozijia_house_detail']
        # for i in new_list:
        #     jobs = [gevent.spawn(self.asyn_message, info) for info in i]
        #     gevent.wait(jobs)
        #     try:
        #         collection.insert_many(list(filter(lambda x: x is not None, [_.value for _ in jobs])))
        #     except:
        #         print('empty')
        # m.connect.close()

        collection = m.connect['friends']['xiaozijia_house_detail']
        # cookie = itertools.cycle([_['cookie'] for _ in user_collection.find(no_cursor_timeout=True)])

        if len([_['cookie'] for _ in user_collection.find(no_cursor_timeout=True)]) == 0:
            time.sleep(120)
        cookie = itertools.cycle([_['cookie'] for _ in user_collection.find(no_cursor_timeout=True)])

        jobs = [gevent.spawn(self.asyn_message, info, cookie) for info in json.loads(body.decode())]
        gevent.wait(jobs)

        try:
            collection.insert_many(list(filter(lambda x: x is not None, [_.value for _ in jobs])))
        except:
            print('empty')
        m.connect.close()
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
