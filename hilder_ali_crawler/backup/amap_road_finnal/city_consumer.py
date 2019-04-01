from gevent import monkey

monkey.patch_all()
import pika
import requests
import json
import gevent
from pymongo import MongoClient
from lib.log import LogHandler
import yaml

setting = yaml.load(open('config_road.yaml'))
rabbit_mq_config = setting['rabbitmq']

log = LogHandler('other_city_consumer')

client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102')

collection_name = setting['mongo']['collection']
collection = client['amap'][collection_name]


class StreetConsume:
    def __init__(self, proxies):
        self.proxies = proxies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_mq_config['host'], port=5673, heartbeat=0))
        self.channel = self.rabbit_connection.channel()
        self.channel.queue_declare(queue=rabbit_mq_config['queue_name'])

    def start_consume(self):
        """
        开始消费amap_tmp队列中的信息，每次分配1个，
        :return:
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=rabbit_mq_config['queue_name'])
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        param = json.loads(body.decode())

        number = param['number']

        number = int(number)
        start_number = 0
        end_number = 0
        self.create_url(start_number, end_number, param)

        jobs = [gevent.spawn(self.async_message, _url) for _url in json.loads(body.decode())]
        gevent.wait(jobs)

    def create_url(self, start_number, end_number, param):
        url_list = []
        for i in range(start_number, end_number):
            city_code = param['city_code']
            street = param['street']

    def async_message(self, param):

        number = param['number']
        region = param['region']
        detail_street = region + street + number + '号'
        map_street = street + number + '号'
        payload = {
            'query_type': 'TQUERY',
            'pagesize': '30',
            'pagenum': '1',
            'qii': 'true',
            'cluster_state': '5',
            'need_utd': 'true',
            'utd_sceneid': '1000',
            'div': 'PC1000',
            'addr_poi_merge': 'true',
            'is_classify': 'true',
            'city': city_code,
            'keywords': detail_street,
        }

        try:
            res = requests.get(self.url, proxies=self.proxies, params=payload, timeout=3)
            # print(res.url)
        except Exception as e:
            log.error(
                '请求失败，url="https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=30&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&city={}&geoobj=121.488683%7C31.21243%7C121.49385%7C31.219216&keywords={}"'.format(
                    payload['city'], payload['keywords']))
            return
        self.check(res, param, map_street)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    def check(res, param, map_street):
        try:
            text = res.json()
        except Exception as e:
            log.error('url={}出现错误，错误原因可能是因为没有poi_list这个字段'.format(res.url))
            return
        if text.get('status') == '1':
            try:
                poi_list = text['data']['poi_list']
            except:
                log.error('url={}出现错误，错误原因可能是因为没有poi_list这个字段'.format(res.url))
                return
            poi_info = []
            for poi in poi_list:
                address = poi['address']
                if map_street in address:
                    dict_text = dict(poi)
                    poi_info.append(dict_text)
                else:
                    break
            if len(poi_info) != 0:
                collection.insert_one(
                    {'poi_info': poi_info, 'city_name': param['city_name'], 'city_code': param['city_code'],
                     'region': param['region'], 'street_number': map_street})
        else:
            print(res.json())
            log.error('请求失败，status不为1，url = {}'.format(res.url))
