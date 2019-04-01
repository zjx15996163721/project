"""
将安居客上所有的城市列表放入到队列中，，，方便请求获取楼盘详情页链接
"""
import requests
from lxml import etree
import pika
import json
from retry import retry
from lib.log import LogHandler

log = LogHandler('test_anjuke_producer_city')

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1',
    port=5673,
    heartbeat=0
))
channel = connection.channel()
channel.queue_declare(queue='anjuke_city_url_list',durable=True)


class VerifyError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

@retry(logger=log,delay=2)
def send_url(proxies):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    url = 'https://www.anjuke.com/sy-city.html'
    requests.get('http://ip.dobel.cn/switch-ip', proxies=proxies)
    res = requests.get(url,headers=headers,proxies=proxies)
    html_res = etree.HTML(res.text)
    a_list = html_res.xpath('//div[@class="letter_city"]/ul/li/div[@class="city_list"]/a')
    print(len(a_list))
    if len(a_list) >0:
        return a_list
    else:
        raise VerifyError('城市列表为空，可能出现滑块验证码')

def analyse_city(proxies):
    a_list = send_url(proxies=proxies)
    for a in a_list:
        city_url = a.xpath('@href')[0]
        channel.basic_publish(
            exchange='',
            routing_key='anjuke_city_url_list',
            body=json.dumps(city_url),
            properties=pika.BasicProperties(delivery_mode=2)
        )


if __name__ == '__main__':
    pass
    # analyse_city(proxies=next(p))





