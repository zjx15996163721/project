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
log = LogHandler('loupan')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['fangjia']['district_complete']


class LouPan:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='loupan')

    def start_crawler(self):
        for page in range(1, 123):
            url = 'http://wuxi.loupan.com/community/' + 'p{}/'.format(str(page))
            self.get_all_url(url)

    def get_all_url(self, page_url):
        print(page_url)
        try:
            r = requests.get(url=page_url, headers=self.headers)
        except Exception as e:
            log.error(e)
            return
        tree = etree.HTML(r.text)
        url_info_list = tree.xpath('/html/body/div[3]/div/div[2]/div[1]/div[@class="item"]')
        for info in url_info_list:
            half_url = info.xpath('./div[1]/h2/a/@href')[0]
            url = 'http://wuxi.loupan.com' + half_url
            region_info = info.xpath('./div[1]/div[1]/div[1]/span/text()')[0]
            region = re.search('\[ (.*) \]', region_info, re.S | re.M).group(1).split(' ')[0]
            data = {
                'url': url,
                'region': region
            }
            self.channel.basic_publish(exchange='',
                                       routing_key='loupan',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))


if __name__ == '__main__':
    loupan = LouPan()
    loupan.start_crawler()
