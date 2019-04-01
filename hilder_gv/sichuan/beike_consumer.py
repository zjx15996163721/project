from gevent import monkey
monkey.patch_all()
import requests
from lxml import etree
import pika
from lib.proxy_iterator import Proxies
from lib.log import LogHandler
from retry import retry
import gevent
import json
import re
from pymongo import MongoClient
from multiprocessing import Process
p = Proxies()
log = LogHandler(__name__)
client = MongoClient(
    host='114.80.150.196',
    port=27777,
    username='goojia',
    password='goojia7102'
)
collection = client['hilder_gv']['beike']
collection.create_index([("city",1),("district_name",1),("region",1),("address",1)],unique=True,name='name_region_addr_city_index')
#楼盘消费者
class LoupanConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }

    def start_consumer(self):
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(self.callback,
                                   queue='beike_loupan',
                                   )
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        loupan_list = json.loads(body.decode())
        if len(loupan_list) == 0:
            print('消息为空')
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            jobs = [gevent.spawn(self.analyse_field,url) for url in loupan_list]
            gevent.wait(jobs)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def analyse_field(self,url):
        loupan_dict = {}
        res = self.send_url(url)
        res_text = res.text
        result = re.search('<a class="s-city" data-xftrack="10124" title="选择城市">(.*?)</a>',res_text,re.S|re.M)
        if result:
            city = result.group(1)
        else:
            city = None
        res_html = etree.HTML(res_text)
        try:
            district_name = res_html.xpath('//div[@class="title-wrap"]/div/h2/text()')[0]
            district_name = district_name.split(' ')
            district_name = ''.join(district_name)
        except Exception as e:
            district_name = None
        #https://leshan.fang.ke.com/loupan/p_bcbiiqc/xiangqing/
        detail_url = url + 'xiangqing/'
        detail_res = self.send_url(detail_url)
        detail_html = etree.HTML(detail_res.text)
        li_list = detail_html.xpath('//ul[@class="x-box"]/li')
        for li in li_list:
            tag = li.xpath('span[@class="label"]/text()')[0]
            print(tag)
            if tag == '区域位置：':
                try:
                    region = li.xpath('span[@class="label-val"]//text()')
                    region = ''.join(region)
                    loupan_dict['region'] = region
                except Exception as e:
                    log.error('{}木有获取到区域位置'.format(url))

            if tag == '楼盘地址：':
                try:
                    address = li.xpath('span[@class="label-val"]//text()')[0]
                    loupan_dict['address'] = address
                except Exception as e:
                    log.error('{}木有获取到楼盘地址'.format(url))
            if tag == '规划户数：':
                try:
                    house_hold_count = li.xpath('span[@class="label-val"]//text()')[0]
                    loupan_dict['house_hold_count'] = house_hold_count
                except Exception as e:
                    log.error('{}木有获取到规划户数'.format(url))
            if tag == '物业费：':
                try:
                    estate_charge = li.xpath('span[@class="label-val"]//text()')[0]
                    loupan_dict['estate_charge'] = estate_charge
                except Exception as e:
                    log.error('{}木有获取到物业费'.format(url))
        loupan_dict['city'] = city
        loupan_dict['district_name'] = district_name
        loupan_dict['url'] = url
        loupan_dict['source'] = 'beike'
        collection.insert(loupan_dict)

    @retry(delay=2,logger=log)
    def send_url(self,url):
        res = requests.get(url,headers=self.headers,proxies=next(p))
        return res




#小区消费者
class DistrictConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }

    def start_consumer(self):
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(self.callback,
                                   queue='beike_district',
                                   )
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        district_list = json.loads(body.decode())
        if len(district_list) == 0:
            print('消息为空')
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            jobs = [gevent.spawn(self.analyse_field,url) for url in district_list]
            gevent.wait(jobs)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def analyse_field(self,url):
        district_dict = {}
        res = self.send_url(url)
        res_text = res.text
        result = re.search("city_name: '(.*?)',", res_text, re.S | re.M)
        if result:
            city = result.group(1)
        else:
            city = None
        res_html = etree.HTML(res_text)
        try:
            district_name = res_html.xpath('//div[@class="title"]/h1/text()')[0]
            district_name_list = district_name.split(' ')
            district_name = ('').join(district_name_list)
            district_name_list = district_name.split('\n')
            district_name = ('').join(district_name_list)
        except Exception as e:
            district_name = None
        try:
            address = res_html.xpath('//div[@class="title"]/div[@class="sub"]/text()')[0]
            address_list = address.split(' ')
            address = ('').join(address_list)
            address_list = address.split('\n')
            address = ('').join(address_list)
            region = address
        except Exception as e:
            address = None
            region = None
        div_list = res_html.xpath('//div[@class="xiaoquDescribe fr"]/div[@class="xiaoquInfo"]/div')
        for div in div_list:
            tag = div.xpath('span[@class="xiaoquInfoLabel"]/text()')[0]
            print(tag)
            tag_list = tag.split(' ')
            tag = ('').join(tag_list)
            print(tag)
            if tag == '房屋总数':
                try:
                    house_hold_count = div.xpath('span[@class="xiaoquInfoContent"]/text()')[0]
                    district_dict['house_hold_count'] = house_hold_count
                except Exception as e:
                    log.error('{}木有获取到房屋总数'.format(url))
            if tag == '物业费用':
                try:
                    estate_charge = div.xpath('span[@class="xiaoquInfoContent"]/text()')[0]
                    estate_charge = estate_charge.split(' ')
                    estate_charge = ''.join(estate_charge)
                    estate_charge = estate_charge.split('\n')
                    estate_charge = ''.join(estate_charge)
                    district_dict['estate_charge'] = estate_charge
                except Exception as e:
                    log.error('{}木有获取到物业费用'.format(url))

        district_dict['city'] = city
        district_dict['district_name'] = district_name
        district_dict['address'] = address
        district_dict['region'] = region
        district_dict['url'] = url
        district_dict['source'] = 'beike'
        collection.insert(district_dict)

    @retry(delay=2,logger=log)
    def send_url(self,url):
        res = requests.get(url,headers=self.headers,proxies=next(p))
        return res



if __name__ == '__main__':
    Process(target=LoupanConsumer().start_consumer).start()
    Process(target=DistrictConsumer().start_consumer).start()
