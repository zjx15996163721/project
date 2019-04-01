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
import threading
log = LogHandler('fangtianxia')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['gv_merge']


class FangTianXiaConsumer:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='fangtianxia_wuye')

    def final_parse(self, data):
        url = data['url']
        print(url)
        name = data['name']
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
            text = r.content.decode('gbk')
            tree = etree.HTML(text)
        except Exception as e:
            self.channel.basic_publish(exchange='',
                                       routing_key='fangtianxia_wuye',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))
            log.error(e)
            return
        try:
            city = tree.xpath('//*[@id="dsy_H01_01"]/div[1]/a/text()')[0]
        except:
            return
        try:
            region_info = re.search('所属区域.*?</strong>(.*?)</dd>', text, re.S | re.M).group(1)
            region = region_info.split(' ')[0]
        except:
            return
        try:
            household_count_info = re.search('房屋总数.*?</strong>(.*?)</dd>', text, re.S | re.M).group(1)
            household_count = re.search('(\d+)', household_count_info, re.S | re.M).group(1)
        except:
            household_count = None
        try:
            estate_charge = re.search('物 业 费.*?</strong>(.*?)元', text, re.S | re.M).group(1)
        except:
            estate_charge = None
        try:
            address = re.search('小区地址.*?</strong>(.*?)</dd>', text, re.S | re.M).group(1)
        except:
            address = None
        try:
            complete_time = re.search('建筑年代.*?</strong>(\d+)年', text, re.S | re.M).group(1)
        except:
            complete_time = None
        data = {
            'source': 'fangtianxia',
            'city': city,
            'region': region,
            'district_name': name,
            'complete_time': complete_time,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address
        }
        if not crawler_collection.find_one({'source': 'fangtianxia', 'city': city, 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            crawler_collection.find_one_and_update({'source': 'fangtianxia', 'city': city, 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}, {'$set': {'complete_time': complete_time}})
            log.info('更新竣工时间{}'.format(complete_time))

    def callback(self, ch, method, properties, body):
        info = json.loads(body.decode())
        self.final_parse(info)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='fangtianxia_wuye')
        self.channel.start_consuming()


if __name__ == '__main__':
    for i in range(80):
        fangtianxiaconsumer = FangTianXiaConsumer()
        threading.Thread(target=fangtianxiaconsumer.start_consuming).start()



