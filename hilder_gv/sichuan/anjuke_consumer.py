import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
import time
import pika
import json
import threading
log = LogHandler('anjuke')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['gv_merge']


class AnJuKeConsumer:

    def __init__(self):
        self.headers = {
            'upgrade-insecure-requests': '1',
            'cookie': 'aQQ_ajkguid=75D77C2A-F680-B489-349F-906930217233; lps=http%3A%2F%2Fshanghai.anjuke.com%2Fcommunity%2Fpudong%2F%7C; twe=2; sessid=E18EB609-6C8E-818B-7EED-C86C2FD5AC83; 58tj_uuid=dea223f6-6b4a-48f1-92af-01ee6a85f34d; init_refer=; new_uv=1; als=0; new_session=0; _ga=GA1.2.1395916484.1545029002; _gid=GA1.2.1022907573.1545029002; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-b; ctid=46; wmda_uuid=09ced73898e209093026d9a297fe1372; wmda_new_uuid=1; wmda_session_id_6289197098934=1545033749144-6ef4fcc0-3c40-26a2; wmda_visited_projects=%3B6289197098934; __xsptplusUT_8=1; __xsptplus8=8.1.1545028464.1545033826.309%234%7C%7C%7C%7C%7C%23%23O0T93MI8LRY7Mmh5GelYb6PAJEBZE-2Y%23',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='anjuke')

    def parse(self, data):
        url = data['url']
        print(url)
        name = data['name']
        try:
            r =requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error('请求失败　url={}, e={}'.format(url, e))
            self.channel.basic_publish(exchange='',
                                       routing_key='anjuke',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))
            return

        if '系统检测到您正在使用网页抓取工具访问安居客网站' in r.text or '访问验证－安居客' in r.text:
            self.channel.basic_publish(exchange='',
                                       routing_key='anjuke',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))
            return
        try:
            tree = etree.HTML(r.text)
            city = tree.xpath('/html/body/div[2]/div[2]/a[2]/text()')[0].replace('小区', '')
            region = tree.xpath('/html/body/div[2]/div[2]/a[3]/text()')[0].replace('小区', '')
            address = tree.xpath('/html/body/div[2]/div[3]/div[1]/h1/span/text()')[0]
        except Exception as e:
            self.channel.basic_publish(exchange='',
                                       routing_key='anjuke_wuyefei',
                                       body=json.dumps(data))
            log.error('没有取到城市　url={}, e={}'.format(url, e))
            log.info('放队列 {}'.format(data))
            return
        try:
            estate_charge_info = tree.xpath('//*[@id="basic-infos-box"]/dl/dd[2]/text()')[0]
            estate_charge = re.search('(\d+\.?\d+?)', estate_charge_info, re.S | re.M).group(1)
        except:
            estate_charge = None
        try:
            household_count_info = tree.xpath('//*[@id="basic-infos-box"]/dl/dd[4]/text()')[0]
            household_count = re.search('(\d+)', household_count_info, re.S | re.M).group(1)
        except:
            household_count = None
        try:
            complete_time_info = tree.xpath('//*[@id="basic-infos-box"]/dl/dd[5]/text()')[0]
            complete_time = re.search('(\d+)', complete_time_info, re.S | re.M).group(1)
        except:
            complete_time = None
        data = {
            'source': 'anjuke',
            'city': city,
            'region': region,
            'district_name': name,
            'complete_time': complete_time,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address,
            'estate_type2': '普通住宅',
        }
        if not collection.find_one(data):
            collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        self.parse(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='anjuke')
        self.channel.start_consuming()


if __name__ == '__main__':
    for i in range(80):
        anjuke = AnJuKeConsumer()
        threading.Thread(target=anjuke.start_consuming).start()

