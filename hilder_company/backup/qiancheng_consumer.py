# -*- coding: utf-8 -*-
# @Time    : 2018/7/24 11:04
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : qiancheng_consumer.py
# @Software: PyCharm

import pika
import requests
from lxml import etree
import re
from company_info import Company
from lib.proxy_iterator import Proxies
import random
import gevent
import json
from lib.proxy_iterator import Proxies

class Data_fetch(object):
    def __init__(self,proxies):
        self.headers = {
            'Host': 'jobs.51job.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',port=5673))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='51job', durable=True)
        self.proxies = proxies

    def data_fetch(self, url):

        response = requests.get(url=url,proxies=self.proxies,headers=self.headers)
        print(url)
        if response.status_code == 200:
            response.encoding = 'GBK'
            tree = etree.HTML(response.text)
            company_id = re.search('https://jobs\.51job\.com/all/co(\d+)\.html', url).group(1)
            company_source = '51job'
            company = Company(company_id=company_id,company_source=company_source)
            try:
                address1 = tree.xpath("/html/body/div[2]/div[2]/div[3]/div[2]/div/p/text()")[1]
                address2 = address1.replace(' ', '').replace('\n', '')
                if '(' in address2:
                    address = address2.split('(')[0]
                else:
                    address = address2
                company_info = tree.xpath("//div[@class='con_txt']/text()")[0]
                company_size_business = tree.xpath("//p[@class='ltype']/text()")[0]
                company_size_business = company_size_business.split('|')
                if len(company_size_business) > 2:
                    company_size = company_size_business[1]
                    business = company_size_business[2]
                else:
                    company_size = company_size_business[0]
                    business = company_size_business[1]
                company.address = address
                company.company_info = company_info
                company.business = business
                company.company_size = company_size
            except Exception as e:
                print(e)
            company_name = tree.xpath("//div[@class='tHeader tHCop']/div[1]/h1/text()")[0]
            company.company_id = company_id
            company.company_name = company_name
            company.company_source = company_source
            company.url = url
            company.insert_db()
        else:
            print(response.status_code)

    def callback(self,ch, method, properties, body):

        jobs = [gevent.spawn(self.data_fetch, url) for url in json.loads(body.decode())]
        gevent.wait(jobs)
        # gevent.joinall(jobs)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        #之前的代码
        # self.data_fetch(body.decode())
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    def comsume_start(self):
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(self.callback, queue='51job')
        self.channel.start_consuming()


    def start_crawler(self):
        self.comsume_start()


# if __name__ == '__main__':
#     data = Data_fetch()
#     data.start_crawler()




