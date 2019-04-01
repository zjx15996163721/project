import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
log = LogHandler('wuxihouse')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['fangjia']['district_complete']


class WuXiHouse:

    def __init__(self):
        self.headers = {
            'Host': 'www.wxhouse.com:6060',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = 'http://www.wxhouse.com:6060/listpros'

    def start_crawler(self):
        for page in range(1, 68):
            data = {
                'proserh.disCode': '',
                'proserh.disIcon': '',
                'proserh.price': '',
                'proserh.houType': '',
                'proserh.status': '',
                'pager.currentPage': page,
                'proserh.proName': '',
                'proserh.orderr': 'createtime'
            }
            try:
                r = requests.post(url=self.start_url, data=data, headers=self.headers, proxies=p)
            except Exception as e:
                continue
            tree = etree.HTML(r.text)
            url_info = tree.xpath("//form[@id='serhform']/div[@class='w1200'][3]/div[@class='fyarea']")
            for info in url_info:
                link = info.xpath("./div[2]/div[1]/a/@href")[0]
                district_name = info.xpath("./div[2]/div[1]/a/span/text()")[0]
                half_link = re.search('showpro\?(.*)', link, re.S | re.M).group(1)
                address = info.xpath('./div[2]/div[2]/text()')[0].replace('地　址：', '').replace('\r', '').replace('\n', '').replace('\t', '')
                url ='http://www.wxhouse.com:6060/showprodetail?' + half_link
                self.parse(url, district_name, address)

    def parse(self, url, district_name, address):
        try:
            r = requests.post(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error('请求失败　url={}, e={}'.format(url, e))
            return
        tree = etree.HTML(r.text)
        try:
            region = tree.xpath('/html/body/div[7]/div[2]/div[1]/li[4]/text()')[0]
        except:
            region = None
        try:
            total_house_info = tree.xpath('/html/body/div[7]/div[2]/div[1]/li[10]/text()')[0]
            household_count = re.search('(\d+)', total_house_info, re.S | re.M).group(1)
        except:
            household_count = None
        try:
            property_fee_info = tree.xpath('/html/body/div[7]/div[2]/div[2]/li[12]/text()')[0]
            estate_charge = re.search('(\d+\.?\d+?)', property_fee_info, re.S | re.M).group(1)
        except:
            estate_charge = None
        data = {
            'source': 'wxhouse',
            'city': '无锡',
            'region': region,
            'district_name': district_name,
            'complete_time': None,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address
        }
        if not collection.find_one(data):
            collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


if __name__ == '__main__':
    wuxi = WuXiHouse()
    wuxi.start_crawler()