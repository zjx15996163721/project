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
collection = m['hilder_gv']['fangtianxia']

top_city_list = ['上海', '北京', '广州', '深圳', '天津',
                 '无锡', '西安', '武汉', '大连', '宁波',
                 '南京', '沈阳', '苏州', '青岛', '长沙',
                 '成都', '重庆', '杭州', '厦门']


class FangTianXia:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = [
            'http://sh.esf.fang.com/housing/',
            'http://esf.fang.com/housing/',
            'http://gz.esf.fang.com/housing/',
            'http://sz.esf.fang.com/housing/',
            'http://tj.esf.fang.com/housing/',
            'http://wuxi.esf.fang.com/housing/',
            'http://xian.esf.fang.com/housing/',
            'http://wuhan.esf.fang.com/housing/',
            'http://dl.esf.fang.com/housing/',
            'http://nb.esf.fang.com/housing/',
            'http://nanjing.esf.fang.com/housing/',
            'http://sy.esf.fang.com/housing/',
            'http://suzhou.esf.fang.com/housing/',
            'http://qd.esf.fang.com/housing/',
            'http://cs.esf.fang.com/housing/',
            'http://cd.esf.fang.com/housing/',
            'http://cq.esf.fang.com/housing/',
            'http://hz.esf.fang.com/housing/',
            'http://xm.esf.fang.com/housing/',
        ]

    def start_crawler(self):
        for url in self.start_url:
            threading.Thread(target=self.start_request, args=(url,)).start()

    def start_request(self, url):
            r = requests.get(url=url, headers=self.headers, proxies=p)
            tree = etree.HTML(r.text)
            region_url_list = tree.xpath('//*[@id="houselist_B03_02"]/div[1]/a')
            for region_url in region_url_list:
                half_region_link = region_url.xpath('./@href')[0]
                try:
                    region_link = url + re.search('/housing/(\d+__0_0_0_0_1_0_0_0/)', half_region_link, re.S | re.M).group(1)
                except:
                    continue
                self.get_max_page(region_link)

    def get_max_page(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        tree = etree.HTML(r.text)
        max_page_info = tree.xpath('//*[@id="houselist_B14_01"]/span/text()')[0]
        max_page = re.search('(\d+)', max_page_info, re.S | re.M).group(1)
        for page in range(1, int(max_page)+1):
            page_url = re.search('(.*?housing/\d+__0_0_0_0_)', url, re.S | re.M).group(1) + str(page) + '_0_0_0/'
            self.get_all_url(page_url)

    def get_all_url(self, url):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        channel = connection.channel()
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        tree = etree.HTML(r.text)
        all_url_info = tree.xpath('//div[@class="houseList"]/div')
        for url_info in all_url_info:
            try:
                detail_url = url_info.xpath('./dl/dd/p[1]/a[1]/@href')[0]
            except:
                continue
            name = url_info.xpath('./dl/dd/p[1]/a[1]/text()')[0]
            if 'esf' in detail_url:
                final_url = 'http:' + re.search('(.*?)esf/', detail_url, re.S | re.M).group(1) + 'xiangqing/'
                data = {
                    'url': final_url,
                    'name': name
                }
                channel.queue_declare(queue='fangtianxia_wuye')
                channel.basic_publish(exchange='',
                                      routing_key='fangtianxia_wuye',
                                      body=json.dumps(data))
                log.info('放队列 {}'.format(data))
            else:
                final_url = 'http:' + detail_url + 'xiangqing/'
                data = {
                    'url': final_url,
                    'name': name
                }
                channel.queue_declare(queue='fangtianxia_wuye')
                channel.basic_publish(exchange='',
                                      routing_key='fangtianxia_wuye',
                                      body=json.dumps(data))
                log.info('放队列 {}'.format(data))
        connection.close()


if __name__ == '__main__':
    fangtianxia = FangTianXia()
    fangtianxia.start_crawler()
