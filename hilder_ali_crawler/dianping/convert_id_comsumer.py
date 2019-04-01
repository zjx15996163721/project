# # -*- coding: utf-8 -*-
# # @Time    : 2018/8/16 16:29
# # @Author  : zjx
# # @Email   : zhangjinxiao@fangjia.com
# # @File    : convert_id_comsumer.py
# # @Software: PyCharm

from pymongo import MongoClient
import requests
import pika
import json
from lib.proxy_iterator import Proxies
from lxml import etree
import re
import yaml
from lib.log import LogHandler

log = LogHandler(__name__)
p = Proxies()

setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='dianping_no_id')


class ConvertId(object):
    def __init__(self, proxies):
        self.proxies = proxies
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            }

    def convert_id(self, new_body):
        name = new_body['name']
        matchText = new_body['matchText']
        cityId = new_body['cityId']
        url = 'https://m.dianping.com/shoplist/{}/search?from=m_search&keyword={}{}'.format(cityId, matchText, name)
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            tree = etree.HTML(r.text)
            shop_link = tree.xpath("//ul[@class='list-search']/li/a/@href")
            if len(shop_link) == 1:
                shop_id = re.search('//m\.dianping\.com/shop/(\d+)\?from=(.*)', shop_link[0]).group(1)
                print(shop_id)
                new_body.update({'id': shop_id})
                dianping_all_type_collection.insert_one(new_body)
                print('插入一条数据 {}'.format(new_body))
            else:
                for link in shop_link:
                    shop_id = re.search('//m\.dianping\.com/shop/(\d+)\?from=(.*)', link).group(1)
                    print(shop_id)
                    if dianping_all_type_collection.find_one({"id": shop_id}) is None:
                        new_body.update({'id': shop_id})
                        dianping_all_type_collection.insert_one(new_body)
                        print('插入一条数据 {}'.format(new_body))
                        break
                    else:
                        print("已经存在库中")
                        continue
        except Exception as e:
            log.error('请求失败,切换代理={}'.format(url))
            self.proxies = next(p)

    def callback(self, ch, method, properties, body):
        new_body = json.loads(body.decode())
        self.convert_id(new_body)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='dianping_no_id')
        channel.start_consuming()
