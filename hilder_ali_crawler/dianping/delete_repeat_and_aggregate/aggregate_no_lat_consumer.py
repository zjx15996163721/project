"""
消费队列中没有经纬度的ID，将经纬度补充上
"""
from pymongo import MongoClient
import yaml
import pika
import json
import requests
import re
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
p = p.get_one(proxies_number=6)
log = LogHandler(__name__)
setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port'], heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='dianping_no_lat', durable=True)


class ConvertLat(object):
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
            'Cookie': 'cy=1; cye=shanghai; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=1665153762cc8-0b288135f9f596-3c7f0257-1fa400-1665153762cc8; _lxsdk=1665153762cc8-0b288135f9f596-3c7f0257-1fa400-1665153762cc8; m_flash2=1; cityid=1; PHOENIX_ID=0a4ca66f-1665153e2f9-4dd3ea; _tr.u=DGLrcBTRs4WIa31f; _tr.s=HyEv9gAf3GKEFCKz; _hc.v=1f6e9b25-9365-df44-9039-7d18cfb90fa5.1538962744; pvhistory="6L+U5ZuePjo8L3N0YXRpY3Rlc3QvbG9nZXZlbnQ/bmFtZT1XaGVyZUFtSUZhaWwmaW5mbz1odG1sLSU1QiU3QiUyMmNvZGUlMjIlM0EyJTJDJTIybWVzc2FnZSUyMiUzQSUyMk5ldHdvcmslMjBsb2NhdGlvbiUyMHByb3ZpZGVyJTIwYXQlMjAlMjdodHRwcyUzQSUyRiUyRnd3dy5nb29nbGVhcGlzLmNvbSUyRiUyNyUyMCUzQSUyME5vJTIwcmVzcG9uc2UlMjByZWNlaXZlZC4lMjIlN0QlNUQmY2FsbGJhY2s9V2hlcmVBbUkxMTUzODk2Mjc0NjM2MD46PDE1Mzg5NjI3NDYzMzddX1s="; msource=default; default_ab=index%3AA%3A1%7CshopList%3AA%3A1; logan_custom_report=; logan_session_token=3pe5xbpfe4pzm8xaog6b; _lxsdk_s=16651706023-351-36e-391%7C%7C87'
        }
        self.proxies = proxies

    def convert_lat(self, shop_id):
        try:
            url = 'https://m.dianping.com/shop/{}/map'.format(shop_id)
            print(url)
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            print(r.status_code)
            info = re.search('PAGE_INITIAL_STATE(.*?)</script>', r.text, re.S | re.M).group(1)
            lat = re.search('"shopLat":(.*?),', info, re.S | re.M).group(1)
            lng = re.search('"shopLng":(.*?),', info, re.S | re.M).group(1)
            dianping_all_type_collection.update_one({'id': shop_id}, {'$set': {'info': info, 'lat': lat, 'lng': lng}})
            print('更新一条数据，将经纬度补上 lat={},lng={},info={}'.format(lat, lng, info))
        except Exception as e:
            log.error('请求失败 url={}, e={}'.format('https://m.dianping.com/shop/{}/map'.format(shop_id), e))
            # channel.basic_publish(exchange='',
            #                       routing_key='dianping_no_lat',
            #                       body=json.dumps(shop_id),
            #                       properties=pika.BasicProperties(delivery_mode=2, ))

    def callback(self, ch, method, properties, body):
        shop_id = json.loads(body.decode())
        self.convert_lat(shop_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_all_shop_id(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='dianping_no_lat')
        print('开始消费ID')
        channel.start_consuming()


if __name__ == '__main__':
    ConvertLat = ConvertLat(p)
    ConvertLat.consume_all_shop_id()