# coding=gbk
import aiohttp
import asyncio
import json
import pika
from lib.log import LogHandler
from pymongo import MongoClient
m = MongoClient(host='192.168.0.136', port=27017)
collection_seaweed = m['fangjia']['seaweed']

n = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_city_list = n['fangjiaguanjia']['city_list']
log = LogHandler(__name__)


class GuanJia:

    def __init__(self):
        self.start_url = 'http://api.cityhouse.cn/csfc/v2/ha/parse/addressmore'
        self.headers = {
            'User-Agent': '%E6%88%BF%E4%BB%B7%E7%AE%A1%E5%AE%B6/2220 CFNetwork/902.2 Darwin/17.7.0'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='guanjia')
        self.cityname_list = []

    def start_crawler(self):
        loop = asyncio.get_event_loop()
        tasks = [self.run(info) for info in self.cityname_list]
        loop.run_until_complete(asyncio.wait(tasks))

    async def run(self, info):
        await self.start_request(info)

    async def start_request(self, info):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.start_url,
                                   params={'apiKey': '2wU0pXPAlX5gpIEph9uvR5',
                                           's': info[0],
                                           'orderCity': info[1]},
                                   headers=self.headers) as response:
                if response.status == 200:
                    await self.get_info(await response.text())
                else:
                    log.error('请求失败')

    async def get_info(self, r):
        print(r)
        info_list = json.loads(r)['position']
        if info_list:
            for info in info_list:
                await self.insert_db(info)

    async def insert_db(self, data):
        if not collection_city_list.find_one({'haCode': data['haCode']}):
            collection_city_list.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        if len(self.cityname_list) == 500:
            self.start_crawler()
            self.cityname_list.clear()
        else:
            self.cityname_list.append(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='guanjia')
        self.channel.start_consuming()


if __name__ == '__main__':
    guanjia = GuanJia()
    guanjia.start_consuming()

