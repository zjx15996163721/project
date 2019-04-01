from gevent import monkey

monkey.patch_all()
import pika
import requests
import json
from pymongo import MongoClient
from lib.log import LogHandler
import yaml
import gevent
from lib.proxy_iterator import Proxies

setting = yaml.load(open('config_road.yaml'))
rabbit_mq_config = setting['rabbitmq']

log = LogHandler('online_other_city_consumer_10_9')



client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102',
                     connect=False)

collection_name = setting['mongo']['collection']
collection = client['amap'][collection_name]

# 队列中一个列表放20个字典的消费方式
class StreetConsume:
    def __init__(self,proxies):
        self.proxies = proxies
        self.headers = {
            'Cookie': 'guid=7a2b-e4a0-254b-11c5; cna=i/YpFOjQczwCAWXgEAt5+FYJ; UM_distinctid=16619d4e2194f6-0ac3308713f79-3c7f0257-140000-16619d4e21a234; _uab_collina=153803167480376613790612; key=bfe31f4e0fb231d29e1d3ce951e2c780; CNZZDATA1255626299=787519963-1538028684-https%253A%252F%252Fwww.baidu.com%252F%7C1539316507; _umdata=6AF5B463492A874DF795A3C884C44A15A9B62757D7DF25F615FB1B7B56E61350FFD51FFBFD2AF40CCD43AD3E795C914CFDF7EF1731B8272D5A4DA2DDC19DFDF3; x5sec=7b22617365727665723b32223a223366383365313137626566383834613062633734376164643039366438646564434b5867674e3446454f326530376e697361727a52673d3d227d; isg=BISEZ-wFg7cqlDcXzi_t1f5FVQu2NaINJJKLT54lnM8SySaT2KxOl5NnDSG0UeBf',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_mq_config['host'], port=5673))
        self.channel = self.rabbit_connection.channel()
        self.channel.queue_declare(queue=rabbit_mq_config['queue_name'])

    def start_consume(self):
        """
        开始消费amap_tmp队列中的信息，每次分配1个
        :return:
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=rabbit_mq_config['queue_name'])
        self.channel.start_consuming()


    def callback(self, ch, method, properties, body):
        params = json.loads(body.decode())
        # job = [gevent.spawn(self.send_url, param) for param in params]
        # gevent.wait(job)

        for x in range(5):
            min_num = x*20
            max_num = (x+1)*20
            job = [gevent.spawn(self.send_url, param) for param in params[min_num:max_num]]
            gevent.wait(job)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_url(self, param):
        city_code = param['city_code']
        street = param['street']
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
            'keywords': detail_street
        }
        try:
            res = requests.get(self.url, headers=self.headers, proxies=self.proxies, params=payload, timeout=3)
        except Exception as e:
            log.error(
                '请求失败，url="https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=30&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&city={}&geoobj=121.488683%7C31.21243%7C121.49385%7C31.219216&keywords={}"'.format(
                    payload['city'], payload['keywords']))
            return
        self.check(res, param, map_street)

    @staticmethod
    def check(res, param, map_street):
        try:
            text = res.json()
            # if "/service/poiInfo" in text:
            #     log.error('出现滑块验证码了')
            #     return
        except Exception as e:
            log.error('url={}出现错误，错误原因返回的结果不能转换为json'.format(res.url))
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
                log.info('插入一条数据')
        else:
            print(res.json())
            log.error('请求成功，但是status不为1，url = {}'.format(res.url))
