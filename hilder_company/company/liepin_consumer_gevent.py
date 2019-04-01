"""
第二种消费者,利用阿布云服务器,控制20并发
"""
import re
import requests
from company_info import Company
from lxml import etree
from lib.log import LogHandler
import pika
import yaml
import json
import gevent

log = LogHandler('liepin_consumer_gevent')
setting = yaml.load(open('config.yaml'))

# connection = pika.BlockingConnection(pika.ConnectionParameters(
#             host=setting['rabbitmq']['host'],
#             port=setting['rabbitmq']['port'],
#             heartbeat=0
#         ))
# channel = connection.channel()
# channel.queue_declare(queue='company_url_queue')

class LiepinConsumeGevent:
    def __init__(self, proxies):
        self.source = 'liepin'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.proxies = proxies
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=setting['rabbitmq']['host'],
            port=setting['rabbitmq']['port'],
            heartbeat=0
        ))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='company_url_queue')

    def start_consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            self.callback,
            queue='company_url_queue'
        )
        self.channel.start_consuming()


    def callback(self, ch, method, properties, body):
        urls = json.loads(body.decode())
        if len(urls) > 40:
            jobs1 = [gevent.spawn(self.send_url, url) for url in urls[:20]]
            gevent.wait(jobs1)
            jobs2 = [gevent.spawn(self.send_url, url) for url in urls[20:40]]
            gevent.wait(jobs2)
            jobs3 = [gevent.spawn(self.send_url, url) for url in urls[40:]]
            gevent.wait(jobs3)
        elif 20 < len(urls) < 40:
            jobs1 = [gevent.spawn(self.send_url, url) for url in urls[:20]]
            gevent.wait(jobs1)
            jobs2 = [gevent.spawn(self.send_url, url) for url in urls[20:]]
            gevent.wait(jobs2)
        else:
            jobs = [gevent.spawn(self.send_url, url) for url in urls]
            gevent.wait(jobs)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_url(self, url):
        try:
            rest = requests.get(url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('{}失败，原因是{}'.format(url, e))
            return
        res = rest.text
        html = etree.HTML(res)
        try:
            company_id = re.search('/company/(\d+)/', url).group(1)
            print(company_id)
            company = Company(company_id, self.source)
            company.url = url
        except Exception as e:
            log.error('缺少必要字段,原因{}'.format(e))
            return

        company_name = html.xpath('//h1/text()')
        if len(company_name) > 0:
            company.company_name = company_name[0]
        address = re.search('data-address="(.*?)"', res)
        if address:
            address = address.group(1)
            print(address)
            company.address = address

        city_list = html.xpath('//div[@class="comp-summary-tag"]/a[@class="comp-summary-tag-dq"]/text()')
        if len(city_list) > 0:
            city = city_list[0]
            company.city = city
        if address:
            region = address
            company.region = region

        business_list = html.xpath('//div[@class="comp-summary-tag"]/a[@data-selector="comp-industry"]/text()')
        if len(business_list) > 0:
            company.business = business_list[0]
        a1_xpath = html.xpath('//div[@class="comp-summary-tag"]/a[1]/text()')
        if len(a1_xpath) > 0:
            string = a1_xpath[0]
            if '人' in string:
                company.company_size = string
            else:
                company.development_stage = string
                a2_xpath = html.xpath('//div[@class="comp-summary-tag"]/a[2]/text()')
                if len(a2_xpath) > 0:
                    size = a2_xpath[0]
                    if '人' in size:
                        company.company_size = size

        text_list = html.xpath("//p[@class='profile']/text()")
        if len(text_list) > 0:
            company_info = ','.join(text_list)
            company.company_info = ''.join(company_info.split())

        if re.search('经营期限：(.*?)</li', res) is not None:
            company.operating_period = re.search('经营期限：(.*?)</li', res).group(1)
            # print(company.operating_period)
        if re.search('注册时间：(.*?)</li', res) is not None:
            company.registration_time = re.search('注册时间：(.*?)</li', res).group(1)
            # print(company.registration_time)
        if re.search('注册资本：(.*?)</li', res) is not None:
            company.registered_capital = re.search('注册资本：(.*?)</li', res).group(1)
            # print(company.registered_capital)
        company.insert_db()
