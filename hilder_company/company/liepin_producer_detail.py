"""
消费猎聘列表页的url,获取每一个公司的url,每一页的所有公司url为一个列表,将列表放入到队列中
"""
import requests
from lxml import etree
from lib.log import LogHandler
import pika
import yaml
import json

log = LogHandler('liepin_producer_detail')
setting = yaml.load(open('config.yaml'))
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=setting['rabbitmq']['host'],
    port=setting['rabbitmq']['port'],
    heartbeat=0
))
channel = connection.channel()
channel.queue_declare(queue='liepin_producer_list')

online_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=setting['rabbitmq']['host'],
    port=setting['rabbitmq']['port'],
    heartbeat=0
))
url_chanel = online_connection.channel()
url_chanel.queue_declare(queue='company_url_queue')


class LiepinProducerDetail:
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.proxies = proxies

    def start_consume(self):
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(
            self.callback,
            queue='liepin_producer_list',
            no_ack=False
        )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.page_parse(json.loads(body.decode()))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # 应该进行的操作是传递url,发起请求，解析公司列表,获取每一个公司的url
    def page_parse(self, url):
        try:
            page_res = requests.get(url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('{}失败，原因是{}'.format(url, e))
            # 切换IP
            requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
            return
        html = etree.HTML(page_res.content.decode())
        company_list = html.xpath("//p[@class='company-name']/a/@href")
        # print(company_list)
        small_list = []
        for company_url in company_list:
            small_list.append(company_url)
        url_chanel.basic_publish(
            exchange='',
            routing_key='company_url_queue',
            body=json.dumps(small_list)
        )
        small_list.clear()
