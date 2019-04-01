import requests
import re
import pika
from lib.log import LogHandler
from pymongo import MongoClient
import datetime
import yaml
import json
log = LogHandler(__name__)

setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
collection_lat = db[setting['mongo']['shop_lat_collection']]
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()


class ShopDetail:
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
            'Cookie': 's_ViewType=10; _lxsdk_cuid=1657fb2c22fc8-0262ece9060c4f-5e452019-1fa400-1657fb2c230c8; _lxsdk=1657fb2c22fc8-0262ece9060c4f-5e452019-1fa400-1657fb2c230c8; _hc.v=296b7cf0-cc73-6d8a-7bf8-f3c8cb83b162.1535445746; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1535453327; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1535467421; logan_custom_report=; msource=default; cityid=2; locallat=51.539466; locallng=-0.6560172; geoType=wgs84; m_flash2=1; default_ab=shop%3AA%3A1%7CshopList%3AA%3A1%7Cmap%3AA%3A1; pvhistory="6L+U5ZuePjo8L3N1Z2dlc3QvZ2V0SnNvbkRhdGE/Y2FsbGJhY2s9anNvbnBfMTUzNTUzNzMwNzkxOV85OTUyNT46PDE1MzU1MzczMDg5MDNdX1s="; logan_session_token=s6gbt95koengxon6pc12; _lxsdk_s=1658518b869-6fd-42-6e8%7C%7C201'
        }
        self.proxies = proxies

    def async_message(self, shop_id):
        try:
            url = 'https://m.dianping.com/shop/{}/map'.format(shop_id)
            print(url)
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            print(r.status_code)
            info = re.search('PAGE_INITIAL_STATE(.*?)</script>', r.text, re.S | re.M).group(1)
            lat = re.search('"shopLat":(.*?),', info, re.S | re.M).group(1)
            lng = re.search('"shopLng":(.*?),', info, re.S | re.M).group(1)
            return info, lat, lng


            # if collection_lat.find_one({"id": shop_id}) is None:
            #     url = 'https://m.dianping.com/shop/{}/map'.format(shop_id)
            #     print(url)
            #     r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            #     print(r.status_code)
            #     info = re.search('PAGE_INITIAL_STATE(.*?)</script>', r.text, re.S | re.M).group(1)
            #     lat = re.search('"shopLat":(.*?),', info, re.S | re.M).group(1)
            #     lng = re.search('"shopLng":(.*?),', info, re.S | re.M).group(1)
            #     collection_lat.insert_one({
            #         'info': info,
            #         'id': shop_id,
            #         'lng': lng,
            #         'lat': lat,
            #         'crawler_time': datetime.datetime.now()                 # 添加爬取时间
            #     })
            #     print("插入一条经纬度 {},{}".format(lat, lng))
            # else:
            #     print('已存在')
        except Exception as e:
            log.error('https://m.dianping.com/shop/{}/map, e={}'.format(shop_id, e))
            return None, None, None

    def callback(self, ch, method, properties, body):
        new_body = json.loads(body.decode())
        self.async_message(new_body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_all_url(self):
        # 消费者给rabbitmq 发送一个信息：在消费者处理完消息之前不要再给消费者发送消息
        channel.basic_qos(prefetch_count=1)
        channel.queue_declare(queue='dianping_id_list')
        channel.basic_consume(self.callback, queue='dianping_id_list')
        print('消费者开启')
        channel.start_consuming()