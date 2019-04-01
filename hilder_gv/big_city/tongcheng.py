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
log = LogHandler('58tongcheng')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['gv_merge']

top_city_list = ['上海', '北京', '广州', '深圳', '天津',
                 '无锡', '西安', '武汉', '大连', '宁波',
                 '南京', '沈阳', '苏州', '青岛', '长沙',
                 '成都', '重庆', '杭州', '厦门']


class TongCheng:

    def __init__(self):
        self.headers = {
            'cookie': 'f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; commontopbar_ipcity=changningx%7C%E9%95%BF%E5%AE%81%7C0; id58=c5/nn1wXQ3A0wzemGmI5Ag==; 58tj_uuid=ac20c541-e164-40e1-9718-be72a9452a47; new_uv=1; utm_source=; spm=; init_refer=; als=0; xxzl_deviceid=1JOCn9ahzkV496HWqiDmLtPpyMp%2FqLfDRox4ARmC2AAe3nOLYPtz7J6sLdUh2EYu; new_session=0; f=n; JSESSIONID=54D1B5AD360417F8F11B455DB234A22B; Hm_lvt_ae019ebe194212c4486d09f377276a77=1545037907,1545037957,1545037977,1545038822; Hm_lpvt_ae019ebe194212c4486d09f377276a77=1545040060; xzfzqtoken=Kk6eVz1jaZJhhM2mlrEeLm3pRRja69vQOWkFfyBjoRgM7c%2B%2FK%2FxBNFJd%2F4Yz1K9Sin35brBb%2F%2FeSODvMgkQULA%3D%3D',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = [
            'https://sh.58.com/xiaoqu/?PGTID=0d00000c-0000-03f6-f953-cb7fb94917aa&ClickID=1',
            'https://bj.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://gz.58.com/xiaoqu/?PGTID=0d00000c-0000-075d-f495-c7a64e7712c7&ClickID=1',
            'https://sz.58.com/xiaoqu/?PGTID=0d00000c-0000-0936-7833-bf473bacf495&ClickID=1',
            'https://tj.58.com/xiaoqu/?PGTID=0d00000c-0000-094e-af24-03399faa01a7&ClickID=1',
            'https://wx.58.com/xiaoqu/?PGTID=0d00000c-0000-0219-0f67-11f17d78fc9a&ClickID=1',
            'https://xa.58.com/xiaoqu/?PGTID=0d00000c-0000-0db3-e650-1d0f5cb01b1f&ClickID=1',
            'https://wh.58.com/xiaoqu/?PGTID=0d00000c-0000-0fd0-c008-9444f7864a12&ClickID=1',
            'https://dl.58.com/xiaoqu/?PGTID=0d00000c-0000-0d06-b956-e866fd87222b&ClickID=1',
            'https://nb.58.com/xiaoqu/?PGTID=0d00000c-0000-0a1a-b420-536c1270e968&ClickID=1',
            'https://nj.58.com/xiaoqu/?PGTID=0d00000c-0000-0289-bedb-f7c32f7e5809&ClickID=1',
            'https://sy.58.com/xiaoqu/?PGTID=0d00000c-0000-0022-eceb-e4b0a58d5f76&ClickID=1',
            'https://su.58.com/xiaoqu/?PGTID=0d00000c-0000-08d0-f7aa-c383dc3fd1ec&ClickID=1',
            'https://qd.58.com/xiaoqu/?PGTID=0d00000c-0000-0fea-efb9-9e88cd8770a2&ClickID=1',
            'https://cs.58.com/xiaoqu/?PGTID=0d00000c-0000-0471-956a-6736580bc404&ClickID=1',
            'https://cd.58.com/xiaoqu/?PGTID=0d00000c-0000-0f11-a721-e525292fff47&ClickID=1',
            'https://cq.58.com/xiaoqu/?PGTID=0d00000c-0000-0218-7a3c-d8901f8c78ac&ClickID=1',
            'https://hz.58.com/xiaoqu/?PGTID=0d00000c-0000-0686-1a45-cd76ac805b05&ClickID=1',
            'https://xm.58.com/xiaoqu/?PGTID=0d00000c-0000-0358-9c64-eb913c4f4378&ClickID=1',
        ]

    def start(self):
        for url in self.start_url:
            threading.Thread(target=self.start_crawler, args=(url, )).start()

    def start_crawler(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        tree = etree.HTML(r.text)
        region_info_list = tree.xpath('//div[@class="filter-wrap"]/dl[1]/dd/a')
        for region_info in region_info_list[1:]:
            region_id = region_info.xpath('./@value')[0]
            region_url = re.search('(https://.*?\.58\.com/xiaoqu/)', url, re.S | re.M).group(1) + region_id + '/pn_1/'
            total_page = self.get_max_page(region_url)
            if total_page:
                for page in range(1, int(total_page) + 1):
                    page_url = re.search('(https://.*?\.58\.com/xiaoqu/\d+/pn_)', region_url, re.S | re.M).group(1) + str(page) + '/'
                    self.get_all_url(page_url)

    def get_max_page(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            print(e)
            return
        try:
            total_page = re.search('totalPage = (\d+);', r.text, re.S | re.M).group(1)
            return total_page
        except Exception as e:
            print(e)
            return

    def get_all_url(self, page_url):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        channel = connection.channel()
        try:
            r = requests.get(url=page_url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        tree = etree.HTML(r.text)
        url_info_list = tree.xpath('//div[@class="content-side-left"]/ul/li')
        for info in url_info_list:
            url = info.xpath('./div[2]/h2/a/@href')[0]
            channel.queue_declare(queue='58tongcheng')
            channel.basic_publish(exchange='',
                                  routing_key='58tongcheng',
                                  body=json.dumps(url))
            log.info('放队列 {}'.format(url))


if __name__ == '__main__':

    tongcheng = TongCheng()
    tongcheng.start()

