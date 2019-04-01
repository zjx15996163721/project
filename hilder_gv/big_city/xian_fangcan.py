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
log = LogHandler('xian')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['xian']


class XiAn:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.start_url_list = [
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=10&page=1', '碑林区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=20&page=1', '莲湖区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=30&page=1', '新城区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=40&page=1', '雁塔区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=50&page=1', '未央区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=60&page=1', '灞桥区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=65&page=1', '高新区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=68&page=1', '曲江新区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=69&page=1', '经济技术开发区'),
            ('http://fgj.xa.gov.cn/esfgp/index.aspx?b1=%25u4F4F%25u5B85&b2&b3=00&b4=00&a1=99&page=1', '其他区县'),
        ]

    def start_crawler(self):
        for i in self.start_url_list:
            # threading.Thread(target=self.start_request, args=(i, )).start()
            self.start_request(i)

    def start_request(self, i):
        region = i[1]
        url = i[0]
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        max_page = tree.xpath('//*[@id="ltl_pagecount"]/text()')[0]
        for page in range(1, int(max_page)+1):
            page_url = url.split('page')[0] + 'page=' + str(page)
            self.get_detail_link(page_url, region)

    def get_detail_link(self, url, region):
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        # print(r.text)
        tree = etree.HTML(r.text)
        info_list = tree.xpath('//div[@id="datalist"]/div[@class="esf_fylb"]')
        for info in info_list:
            half_link = info.xpath('./div[2]/table/tr[1]/td[1]/a/@href')[0]
            detail_url = 'http://fgj.xa.gov.cn/esfgp/' + half_link
            name = info.xpath('./div[2]/table/tr[2]/td[1]/a/font/text()')[0]
            self.get_detail(detail_url, name, region)

    def get_detail(self, url, name, region):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        try:
            complete_time = tree.xpath('//*[@id="lbl_jznf"]/text()')[0]
        except:
            complete_time = None
        try:
            address = tree.xpath('//*[@id="lbl_fbzl"]/text()')[0]
        except:
            address = None
        try:
            estate_type2 = tree.xpath('//*[@id="lbl_yt"]/text()')[0]
        except:
            estate_type2 = None
        try:
            area = tree.xpath('//*[@id="lbl_jzmj"]/text()')[0]
        except:
            area = None
        data = {
            'source': 'xianfang',
            'city': '西安',
            'region': region,
            'district_name': name,
            'complete_time': complete_time,
            'household_count': None,
            'estate_charge': None,
            'address': address,
            'area': area,
            'estate_type2': estate_type2,
        }
        if not crawler_collection.find_one({'source': 'xianfang', 'city': '西安', 'region': region, 'district_name': name,
                                            'complete_time':complete_time, 'estate_charge': None, 'area': area,
                                            'address': address, 'estate_type2': estate_type2}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


if __name__ == '__main__':
    x = XiAn()
    x.start_crawler()






