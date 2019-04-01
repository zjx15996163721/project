import requests
from lxml import etree
import pika
from lib.proxy_iterator import Proxies
from lib.log import LogHandler
from retry import retry
import json
from multiprocessing import Process
p = Proxies()
log = LogHandler(__name__)

class SichuanProducer:
    def __init__(self):
        self.city_base_url_list = ["cd.ke.com", "mianyang.ke.com", "yibin.fang.ke.com", "zg.fang.ke.com","pzh.fang.ke.com",
                                   "leshan.fang.ke.com", "nanchong.ke.com", "luzhou.fang.ke.com", "ziyang.fang.ke.com",
                                   "neijiang.fang.ke.com", "dazhou.ke.com", "bz.fang.ke.com", "sn.fang.ke.com",
                                   "ms.fang.ke.com","dy.fang.ke.com", "ga.fang.ke.com", "yaan.fang.ke.com", "ab.fang.ke.com",
                                   "ganzi.fang.ke.com","liangshan.ke.com"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()

    def start_crawl(self):
        for city_base_url in self.city_base_url_list:
            self.is_has_all(city_base_url)

    #主页
    def zhuye(self,city_base_url):
        # https://nanchong.ke.com/
        main_url = 'https://' + city_base_url + '/'
        while True:
            try:
                res = requests.get(main_url,headers=self.headers,proxies=next(p))
                if res.status_code == 200:
                    html = etree.HTML(res.text)
                    return html,main_url
            except Exception as e:
                log.error('{}请求失败，重试'.format(main_url))

    #判断是否含有楼盘和小区的函数
    def is_has_all(self,city_base_url):
        html,main_url = self.zhuye(city_base_url)
        if 'fang' not in main_url:
            name_list = html.xpath('//div[@class="nav typeUserInfo"]/ul/li/a/text()')
            if '新房' in name_list:
                self.loupan(main_url)
            # if '小区' in name_list:
            #     self.district(main_url)
        else:
            self.loupan(main_url)

    #楼盘
    def loupan(self,main_url):
        # https://cd.fang.ke.com/loupan/
        loupan_url = main_url + 'loupan/'
        res = self.send_url(loupan_url)
        loupan_html = etree.HTML(res.text)
        #获取各个区域
        region_list = loupan_html.xpath('/html/body/div[4]/div[2]/ul/li/@data-district-spell')
        for region in region_list:
            region_url = loupan_url + region + '/'
            region_res = self.send_url(region_url)
            region_html = etree.HTML(region_res.text)
            try:
                total_num = region_html.xpath('//div[@class="resblock-have-find"]/span[@class="value"]/text()')[0]
            except Exception as e:
                log.error('{}没有获取到楼盘总数'.format(region_url))
                return
            if int(total_num) == 0:
                return
            total_page = int(int(total_num)/10)+1
            print(total_page)
            for page in range(total_page+1):
                #https://cd.ke.com/xiaoqu/jinjiang/pg2/
                page_url = region_url + 'pg' + str(page) + '/'
                print(page_url)
                page_res = self.send_url(page_url)
                page_html = etree.HTML(page_res.text)
                loupan_list = page_html.xpath('/html/body/div[5]/ul[2]/li/div/div[1]/a')
                detail_url_list = []
                for small_loupan in loupan_list:
                    loupan_href = small_loupan.xpath('@href')[0]
                    loupan_href = loupan_href.replace('/loupan/','')
                    detail_url = loupan_url + loupan_href
                    detail_url_list.append(detail_url)
                #放入到队列中
                self.channel.queue_declare(queue='beike_loupan')
                self.channel.basic_publish(exchange='', routing_key='beike_loupan', body=json.dumps(detail_url_list))
                detail_url_list.clear()
                print('detail_url_list放入队列')


    #小区
    def district(self,main_url):
        #https://cd.ke.com/xiaoqu/
        district_url =  main_url + 'xiaoqu/'
        res = self.send_url(district_url)
        dis_html = etree.HTML(res.text)
        # 获取各个区域
        region_list = dis_html.xpath('//*[@id="beike"]/div[1]/div[3]/div[1]/dl[2]/dd/div/div/a/@href')
        for region in region_list:
            region = region.replace('/xiaoqu/','')
            region_url = district_url + region
            print(region_url)
            region_res = self.send_url(region_url)
            region_html = etree.HTML(region_res.text)
            try:
                total_num = region_html.xpath('//*[@id="beike"]/div[1]/div[4]/div/div[2]/h2/span/text()')[0]
            except Exception as e:
                log.error('{}没有获取到小区总数'.format(region_url))
                return
            if int(total_num) == 0:
                return
            total_page = int(int(total_num) / 30) + 1
            print(total_page)
            for page in range(total_page + 1):
                # https://cd.ke.com/xiaoqu/jinjiang/pg2/
                page_url = region_url + 'pg' + str(page) + '/'
                print(page_url)
                page_res = self.send_url(page_url)
                page_html = etree.HTML(page_res.text)
                dis_list = page_html.xpath('//*[@id="beike"]/div[1]/div[4]/div/div[3]/ul/li/div[1]/div[1]/a/@href')
                # 放入到队列中
                self.channel.queue_declare(queue='beike_district')
                self.channel.basic_publish(exchange='', routing_key='beike_district', body=json.dumps(dis_list))
                print('dis_list放入队列')

    #发送请求的函数
    @retry(delay=2)
    def send_url(self,url):
        res = requests.get(url,headers=self.headers,proxies=next(p))
        return res

class NewSichuanProducer:
    def __init__(self):
        self.city_base_url_list = ["cd.ke.com", "mianyang.ke.com", "yibin.fang.ke.com", "zg.fang.ke.com","pzh.fang.ke.com",
                                   "leshan.fang.ke.com", "nanchong.ke.com", "luzhou.fang.ke.com", "ziyang.fang.ke.com",
                                   "neijiang.fang.ke.com", "dazhou.ke.com", "bz.fang.ke.com", "sn.fang.ke.com",
                                   "ms.fang.ke.com","dy.fang.ke.com", "ga.fang.ke.com", "yaan.fang.ke.com", "ab.fang.ke.com",
                                   "ganzi.fang.ke.com","liangshan.ke.com"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()

    def start_crawl(self):
        for city_base_url in self.city_base_url_list:
            self.is_has_all(city_base_url)

    #主页
    def zhuye(self,city_base_url):
        # https://nanchong.ke.com/
        main_url = 'https://' + city_base_url + '/'
        while True:
            try:
                res = requests.get(main_url,headers=self.headers,proxies=next(p))
                if res.status_code == 200:
                    html = etree.HTML(res.text)
                    return html,main_url
            except Exception as e:
                log.error('{}请求失败，重试'.format(main_url))

    #判断是否含有楼盘和小区的函数
    def is_has_all(self,city_base_url):
        html,main_url = self.zhuye(city_base_url)
        if 'fang' not in main_url:
            name_list = html.xpath('//div[@class="nav typeUserInfo"]/ul/li/a/text()')
            if '小区' in name_list:
                self.district(main_url)

    #楼盘
    def loupan(self,main_url):
        # https://cd.fang.ke.com/loupan/
        loupan_url = main_url + 'loupan/'
        res = self.send_url(loupan_url)
        loupan_html = etree.HTML(res.text)
        #获取各个区域
        region_list = loupan_html.xpath('/html/body/div[4]/div[2]/ul/li/@data-district-spell')
        for region in region_list:
            region_url = loupan_url + region + '/'
            region_res = self.send_url(region_url)
            region_html = etree.HTML(region_res.text)
            try:
                total_num = region_html.xpath('//div[@class="resblock-have-find"]/span[@class="value"]/text()')[0]
            except Exception as e:
                log.error('{}没有获取到楼盘总数'.format(region_url))
                return
            if int(total_num) == 0:
                return
            total_page = int(int(total_num)/10)+1
            print(total_page)
            for page in range(total_page+1):
                #https://cd.ke.com/xiaoqu/jinjiang/pg2/
                page_url = region_url + 'pg' + str(page) + '/'
                print(page_url)
                page_res = self.send_url(page_url)
                page_html = etree.HTML(page_res.text)
                loupan_list = page_html.xpath('/html/body/div[5]/ul[2]/li/div/div[1]/a')
                detail_url_list = []
                for small_loupan in loupan_list:
                    loupan_href = small_loupan.xpath('@href')[0]
                    loupan_href = loupan_href.replace('/loupan/','')
                    detail_url = loupan_url + loupan_href
                    detail_url_list.append(detail_url)
                #放入到队列中
                self.channel.queue_declare(queue='beike_loupan')
                self.channel.basic_publish(exchange='', routing_key='beike_loupan', body=json.dumps(detail_url_list))
                detail_url_list.clear()
                print('detail_url_list放入队列')


    #小区
    def district(self,main_url):
        #https://cd.ke.com/xiaoqu/
        district_url =  main_url + 'xiaoqu/'
        res = self.send_url(district_url)
        dis_html = etree.HTML(res.text)
        # 获取各个区域
        region_list = dis_html.xpath('//*[@id="beike"]/div[1]/div[3]/div[1]/dl[2]/dd/div/div/a/@href')
        for region in region_list:
            region = region.replace('/xiaoqu/','')
            region_url = district_url + region
            print(region_url)
            region_res = self.send_url(region_url)
            region_html = etree.HTML(region_res.text)
            try:
                total_num = region_html.xpath('//*[@id="beike"]/div[1]/div[4]/div/div[2]/h2/span/text()')[0]
            except Exception as e:
                log.error('{}没有获取到小区总数'.format(region_url))
                return
            if int(total_num) == 0:
                return
            total_page = int(int(total_num) / 30) + 1
            print(total_page)
            for page in range(total_page + 1):
                # https://cd.ke.com/xiaoqu/jinjiang/pg2/
                page_url = region_url + 'pg' + str(page) + '/'
                print(page_url)
                page_res = self.send_url(page_url)
                page_html = etree.HTML(page_res.text)
                dis_list = page_html.xpath('//*[@id="beike"]/div[1]/div[4]/div/div[3]/ul/li/div[1]/div[1]/a/@href')
                # 放入到队列中
                self.channel.queue_declare(queue='beike_district')
                self.channel.basic_publish(exchange='', routing_key='beike_district', body=json.dumps(dis_list))
                print('dis_list放入队列')

    #发送请求的函数
    @retry(delay=2)
    def send_url(self,url):
        res = requests.get(url,headers=self.headers,proxies=next(p))
        return res

if __name__ == '__main__':
    Process(target=SichuanProducer().start_crawl).start()
    Process(target=NewSichuanProducer().start_crawl).start()
    # sichuan = SichuanProducer()
    # sichuan.start_crawl()


