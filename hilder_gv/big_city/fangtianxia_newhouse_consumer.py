import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
import pika
import json
import threading
log = LogHandler('fangtianxia')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['fangtianxia']


class FangTianXiaNewHouseConsumer:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='fangtianxia_newhouse')

    def final_parse(self, data):
        url = data['url']
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        try:
            text = r.content.decode('gbk')
            tree = etree.HTML(text)
        except Exception as e:
            print(e)
            return
        try:
            city = tree.xpath('//*[@id="dsy_H01_01"]/div[1]/a/text()')[0]
        except:
            return
        print(city)
        try:
            region = tree.xpath('//*[@id="xfzxxq_B01_03"]/p/a[3]/text()')[0].replace('楼盘', '')
        except:
            return
        print(region)
        try:
            district_name = tree.xpath('//*[@id="daohang"]/div/div/dl/dd/div[1]/h1/a/text()')[0]
        except:
            return
        print(district_name)
        try:
            household_count = re.search('>(\d+)户', text, re.S | re.M).group(1)
        except:
            household_count = None
        print(household_count)
        try:
            estate_charge_info = tree.xpath('//div[@class="main-item"]/ul/li[9]/div[2]/text()')[0]
            estate_charge = re.search('(.*?)元', estate_charge_info, re.S | re.M).group(1)
        except:
            estate_charge = None
        print(estate_charge)
        try:
            address = re.search('楼盘地址.*?class="list-right-text">(.*?)</div>', text, re.S | re.M).group(1)
        except:
            # address = re.search('楼盘地址.*?class="list-right" title="(.*?)">', text, re.S | re.M).group(1)
            address = None
        print(address)
        data = {
            'source': 'fangtianxia',
            'city': city,
            'region': region,
            'district_name': district_name,
            'complete_time': None,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address,
            'url': url
        }
        if not crawler_collection.find_one({'city': city, 'region': region, 'district_name': district_name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')

    def callback(self, ch, method, properties, body):
        info = json.loads(body.decode())
        self.final_parse(info)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='fangtianxia_newhouse')
        self.channel.start_consuming()


if __name__ == '__main__':
    for i in range(80):
        f = FangTianXiaNewHouseConsumer()
        threading.Thread(target=f.start_consuming).start()

