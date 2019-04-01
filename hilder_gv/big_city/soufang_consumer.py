import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
import aiohttp
import asyncio
from lib.log import LogHandler
import time
import pika
import json
log = LogHandler('soufang')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['fangjia']['district_complete']


class SouFangConsumer:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='soufang')

    def final_parse(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            self.channel.basic_publish(exchange='',
                                       routing_key='soufang',
                                       body=json.dumps(url))
            log.info('放队列 {}'.format(url))
            return
        tree = etree.HTML(r.text)
        try:
            city = tree.xpath('//*[@id="city"]/a/span/text()')[0]
        except:
            return
        print(city)
        try:
            region_info = re.search('所在区域.*?<span>(.*?)</span>', r.text, re.S | re.M).group(1)
            region = region_info.replace('\t', '').split('\r\n')[1]
        except:
            return
        print(region)
        try:
            name = tree.xpath('/html/body/div[5]/div[3]/div[1]/div[2]/h2/text()')[0]
        except:return
        print(name)
        try:
            household_count_info = tree.xpath('/html/body/div[6]/div[1]/div[1]/ul/li[6]/span/text()')[0]
            household_count = re.search('(\d+)', household_count_info, re.S | re.M).group(1)
        except:
            household_count = None
        print(household_count)
        try:
            estate_charge_info = tree.xpath('/html/body/div[6]/div[1]/div[1]/ul/li[12]/span/text()')[0]
            estate_charge = re.search('(\d+\.?\d+?)', estate_charge_info, re.S | re.M).group(1)
        except:
            estate_charge = None
        print(estate_charge)
        try:
            address = tree.xpath('/html/body/div[6]/div[1]/div[1]/ul/li[15]/span/text()')[0]
        except:
            address = None
        print(address)
        data = {
            'source': 'soufang',
            'city': city,
            'region': region,
            'district_name': name,
            'complete_time': None,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address
        }
        if not crawler_collection.find_one({'city': city, 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')

    def callback(self, ch, method, properties, body):
        url = json.loads(body.decode())
        self.final_parse(url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=100)
        self.channel.basic_consume(self.callback, queue='soufang')
        self.channel.start_consuming()


if __name__ == '__main__':
    soufang = SouFangConsumer()
    soufang.start_consuming()