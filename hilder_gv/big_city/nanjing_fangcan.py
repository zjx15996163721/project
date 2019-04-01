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
log = LogHandler('nanjing')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['nanjing']


class Nangjing:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }

    def start_crawler(self):
        start_url = 'http://www.njhouse.com.cn/2016/spf/list.php?dist=&use=1&saledate=0&pgno='
        for page in range(1, 65):
            url = start_url + str(page)
            try:
                r = requests.get(url=url, headers=self.headers, proxies=p)
            except Exception as e:
                print(e)
                continue
            tree = etree.HTML(r.text)
            info_list = tree.xpath('//div[@class="spl_table"]/table')
            for info in info_list:
                half_link = info.xpath('./tbody/tr[1]/td[3]/a/@href')[0]
                detail_link = 'http://www.njhouse.com.cn/2016/spf/' + half_link
                name = info.xpath('./tbody/tr[1]/td[3]/a/text()')[0]
                region = info.xpath('./tbody/tr[2]/td[2]/text()')[0]
                estate_type2 = info.xpath('./tbody/tr[3]/td[2]/text()')[0]
                address = info.xpath('./tbody/tr[4]/td[2]/text()')[0]
                self.get_detail(detail_link, region, name, address, estate_type2)

    def get_detail(self, url, region, name, address, estate_type2):
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        try:
            household_count = tree.xpath('/html/body/div[1]/div[2]/div/div[3]/div/table[1]/tbody/tr[1]/td[2]/text()')[0].replace('套', '')
        except:
            household_count = None
        try:
            area = tree.xpath('/html/body/div[1]/div[2]/div/div[3]/div/table[1]/tbody/tr[2]/td[2]/text()')[0].replace('m', '')
        except:
            area = None
        data = {
            'source': 'nanjingfang',
            'city': '南京',
            'region': region,
            'district_name': name,
            'complete_time': None,
            'household_count': household_count,
            'estate_charge': None,
            'address': address,
            'area': area,
            'estate_type2': estate_type2,
        }
        if not crawler_collection.find_one({'source': 'nanjingfang', 'city': '南京', 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': None, 'area': area,
                                            'address': address, 'estate_type2': estate_type2}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


if __name__ == '__main__':
    n = Nangjing()
    n.start_crawler()

