# from gevent import monkey
# monkey.patch_all()
import requests
from lxml import etree
from pymongo import MongoClient
from lib.log import LogHandler
import datetime
import pika
import json
import yaml
# import gevent
from datetime import datetime, timedelta, timezone
log = LogHandler('wangyi')
setting = yaml.load(open('wangyi_config.yaml'))

m = MongoClient(host=setting['mongo_235']['host'],
                port=setting['mongo_235']['port'],
                username=setting['mongo_235']['user_name'],
                password=setting['mongo_235']['password'])
crawler_collection = m[setting['mongo_235']['db_name']][setting['mongo_235']['collection']]


class WangYiConsumer:

    def __init__(self, proxies):
        self.headers = {
            'Host': 'data.house.163.com',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': 'vjuids=141315b71.16778fc86e6.0.7a85a7026d79a; vjlast=1543923075.1543923075.30; _ntes_nnid=d03c289051f2bddb3c1f67707d0a284c,1543923075313; _ntes_nuid=d03c289051f2bddb3c1f67707d0a284c; scrollPos=0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        }
        self.proxies = proxies
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'],
                                                                            port=setting['rabbit']['port'], heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='wangyi')
        self.data_list = []

    def parse(self, data):
        url = data['url']
        print(url)
        city = data['city']
        date = data['date']
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            self.channel.basic_publish(exchange='',
                                       routing_key='wangyi',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))
            log.error('请求失败 url={}, e={}'.format(url, e))
            return
        try:
            tree = etree.HTML(r.text)
            info_list_mBg2 = tree.xpath('//*[@id="resultdiv_1"]/table/tbody/tr[@class="mBg2"]')
        except Exception as e:
            print(e)
            return
        self.get_info(info_list_mBg2, city, date)

        try:
            tree = etree.HTML(r.text)
            info_list_mBg1 = tree.xpath('//*[@id="resultdiv_1"]/table/tbody/tr[@class="mBg1"]')
        except Exception as e:
            print(e)
            return
        self.get_info(info_list_mBg1, city, date)

    def get_info(self, info_list, city, date):
        for info in info_list:
            try:
                region = info.xpath('./td[4]/text()')[0]
                name = info.xpath('./td[2]/a/text()')[0]
            except:
                continue

            house_num_str = info.xpath('./td[5]/text()')[0]
            house_num = int(house_num_str)

            total_size_str = info.xpath('./td[6]/text()')[0]
            total_size = int(total_size_str)

            avg_price_str = info.xpath('./td[7]/text()')[0].replace(',', '').replace(' ', '')
            if '--' in avg_price_str:
                avg_price = 0
            else:
                avg_price = int(avg_price_str)

            total_price_str = info.xpath('./td[8]/text()')[0].replace(',', '').replace(' ', '')
            if '--' in total_price_str:
                total_price = 0
            else:
                total_price = int(total_price_str)

            his_num_str = info.xpath('./td[9]/text()')[0]
            his_num = int(his_num_str)

            his_size_str = info.xpath('./td[10]/text()')[0]
            his_size = int(his_size_str)

            not_sale_num_str = info.xpath('./td[11]/text()')[0]
            not_sale_num = int(not_sale_num_str)

            not_sale_size_str = info.xpath('./td[12]/text()')[0]
            not_sale_size = int(not_sale_size_str)

            date = int(date)
            resource = '网易房产'

            data = {
                'city': city,
                'region': region,
                'name': name,
                'house_num': house_num,
                'total_size': total_size,
                'avg_price': avg_price,
                'total_price': total_price,
                'date': date,
                'his_num': his_num,
                'his_size': his_size,
                'not_sale_num': not_sale_num,
                'not_sale_size': not_sale_size,
                'resource': resource,
                'c_date': datetime.utcnow().replace(tzinfo=timezone.utc)
            }
            if not crawler_collection.find_one({'city': city, 'region': region, 'name': name,
                                                'resource': resource, 'house_num': house_num,
                                                'total_size': total_size, 'avg_price': avg_price,
                                                'total_price': total_price, 'date': date,
                                                'his_num': his_num, 'his_size': his_size,
                                                'not_sale_num': not_sale_num, 'not_sale_size': not_sale_size}):
                crawler_collection.insert_one(data)
                log.info('插入一条数据{}'.format(data))
            else:
                log.info('重复数据')

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        self.parse(data)
        # self.data_list.append(data)
        # if len(self.data_list) == 50:
        #     tasks = [gevent.spawn(self.parse, d) for d in self.data_list]
        #     gevent.joinall(tasks)
        #     self.data_list.clear()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='wangyi')
        self.channel.start_consuming()


"""
city        城市　     string
region      区域　     string
name        小区名　   string
house_num   成交量     int
total_size  成交总面积 int
total_price 总价　     long
avg_price   均价　     int
date        成交日期　 Date
his_num     历史成交数 int
his_size    历史成交面积int
not_sale_num 未售数量　int
not_sale_size 未售面积　int
resource    来源      　string
c_date      创建时间　  date
"""
