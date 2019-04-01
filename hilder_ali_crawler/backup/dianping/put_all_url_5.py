"""
爬取顺序：城市-区域-街道-菜系
start:5
    消费
"""

import json
from dianping.request_detail import request_get
from lxml import etree
import yaml
import pika
from lib.rabbitmq import Rabbit

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
cooking_queue = setting['dianping']['rabbit']['queue']['cooking_queue']
first_queue = setting['dianping']['rabbit']['queue']['first_queue']
list_queue = setting['dianping']['rabbit']['queue']['list_queue']
channel.queue_declare(queue=cooking_queue)


# 放入html队列
def html_put_in_queue(data):
    channel.basic_publish(exchange='',
                          routing_key=first_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2))


# 放入url队列
def url_put_in_queue(data):
    channel.basic_publish(exchange='',
                          routing_key=list_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2))


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    city_name = body['city_name']
    cooking_url = body['cooking_url']
    region_name = body['region_name']
    street_name = body['street_name']
    kind_code = body['kind_code']
    pinyin = body['pinyin']
    logo = cooking_url.split('/')[-1]
    url = 'http://www.dianping.com/' + pinyin + '/' + kind_code + '/' + logo
    html = request_get(url, ip,connection)
    try:
        tree = etree.HTML(html.content.decode())
        page_list = tree.xpath('//a[@class="PageLink"]')
        if not page_list:
            data1 = {
                'html': html.content.decode(),
                'kind_code': kind_code,
                'city': [city_name, region_name, street_name],
            }
            print('只有一页，url={}'.format(url))
            html_put_in_queue(data1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        data1 = {'html': html.content.decode(),
                 'kind_code': kind_code,
                 'city': [city_name, region_name, street_name]}
        print('放入第一页')
        html_put_in_queue(data1)
        for i in range(2, int(page_list[-1].text) + 1):
            not_first_url = 'http://www.dianping.com/' + pinyin + '/' + kind_code + '/' + logo + 'p' + str(i)
            data2 = {'url': not_first_url,
                     'kind_code': kind_code,
                     'city': [city_name, region_name, street_name]}
            print(data2)
            url_put_in_queue(data2)
    except Exception as e:
        channel.basic_publish(exchange='',
                              routing_key=cooking_queue,
                              body=json.dumps(body),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=cooking_queue, consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-dyn.abuyun.com", "port": "9020",
                                                         "user": "H51910O3VL7534QD", "pass": "42DE00B25FC5330C"}
    consume_start(ip)
