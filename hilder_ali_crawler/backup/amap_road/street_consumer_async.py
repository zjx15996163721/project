"""
将并发gevent改为利用asyncio实现的异步，
在本地测试的时候速度比线上使用的gevent的代码快一点点，在0.4-0.8之间浮动
缺点：异步请求出错的可能性较高
"""
from gevent import monkey

monkey.patch_all()
import pika
import json
from pymongo import MongoClient
from lib.log import LogHandler
import yaml
import time
import aiohttp
import asyncio

setting = yaml.load(open('config_road.yaml'))
rabbit_mq_config = setting['rabbitmq']

log = LogHandler('other_9_27')

client = MongoClient(host='114.80.150.198',
                     port=27017,
                     # username='goojia',
                     # password='goojia7102',
                     connect=False)

collection_name = setting['mongo']['collection']
collection = client['amap'][collection_name]


class StreetConsume:
    def __init__(self, proxies):
        self.proxies = proxies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_mq_config['host'], port=5673))
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
        params = json.loads(body.decode())
        loop = asyncio.get_event_loop()
        tasks = [self.start(param) for param in params]
        loop.run_until_complete(asyncio.wait(tasks))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    async def start(self, param):
        try:
            semaphore = asyncio.Semaphore(100)
            street = param['street']
            number = param['number']
            map_street = street + number + '号'
            await self.check(await self.send_url(param, semaphore), param, map_street)
        except Exception as e:
            print(e)

    async def send_url(self, param, semaphore):
        city_code = param['city_code']
        street = param['street']
        number = param['number']
        region = param['region']
        detail_street = region + street + number + '号'
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
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(self.url, headers=self.headers, proxy=self.proxies['https'], params=payload,
                                           timeout=3) as resp:
                        if resp.status == 200:
                            con = await resp.json()
                            return con
                        else:
                            log.error('请求不成功,状态码为{}'.format(resp.status))
                            print('状态码为{}'.format(resp.status))
                except:
                    log.error(
                        '异步请求失败，url="https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=30&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&city={}&geoobj=121.488683%7C31.21243%7C121.49385%7C31.219216&keywords={}"'.format(
                            payload['city'], payload['keywords']))

    @staticmethod
    async def check(res, param, map_street):
        if res:
            if res.get('status') == '1':
                try:
                    poi_list = res['data']['poi_list']
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
                log.error('请求失败，status不为1，text={}'.format(res))
