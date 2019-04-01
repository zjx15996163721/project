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
log = LogHandler('ningbo')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['gv_merge']


class NingBo:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }

    def start_crawler(self):
        start_url = 'https://newhouse.cnnbfdc.com/project/page_'
        for page in range(1, 101):
            url = start_url + str(page)
            try:
                r = requests.get(url=url, headers=self.headers, proxies=p)
            except Exception as e:
                print(e)
                continue
            tree = etree.HTML(r.text)
            info_list = tree.xpath('//ul[@id="project_list"]/li')
            for info in info_list:
                link = info.xpath('./div[2]/div[1]/b/a/@href')[0]
                detail_url = 'https://newhouse.cnnbfdc.com' + link
                name = info.xpath('./div[2]/div[1]/b/a/text()')[0]
                address = info.xpath('./div[2]/div[2]/div[1]/text()')[0]
                self.get_detail(detail_url, name, address)

    def get_detail(self, url, name, address):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        region = tree.xpath('/html/body/div[2]/div[2]/div[2]/div[3]/ul/li[3]/span[1]/text()')[0]
        realdata_url = 'https://newhouse.cnnbfdc.com/project/realdata?projectGUID=' + url.split('=')[1]
        self.final_parse(realdata_url, name, address, region)

    def final_parse(self, url, name, address, region):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        household_count = tree.xpath('/html/body/div[2]/div[2]/div[2]/div/ul/li[7]/big/text()')[0]
        area = tree.xpath('/html/body/div[2]/div[2]/div[2]/div/ul/li[1]/big/text()')[0].replace('㎡', '')
        data = {
            'source': 'ningbofang',
            'city': '宁波',
            'region': region,
            'district_name': name,
            'complete_time': None,
            'household_count': household_count,
            'estate_charge': None,
            'address': address,
            'area': area,
            'estate_type2': '普通住宅',
        }
        if not crawler_collection.find_one({'source': 'ningbofang', 'city': '宁波', 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': None, 'area': area,
                                            'address': address}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


if __name__ == '__main__':
    n = NingBo()
    n.start_crawler()


