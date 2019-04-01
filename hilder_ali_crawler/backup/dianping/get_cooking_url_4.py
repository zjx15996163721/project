"""
爬取顺序：城市-区域-街道-菜系
start:4
"""

from dianping.request_detail import request_get
from lxml import etree
import json
import yaml
from lib.rabbitmq import Rabbit
import pika

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
street_queue = setting['dianping']['rabbit']['queue']['street_queue']
cooking_queue = setting['dianping']['rabbit']['queue']['cooking_queue']
first_queue = setting['dianping']['rabbit']['queue']['first_queue']
list_queue = setting['dianping']['rabbit']['queue']['list_queue']
channel.queue_declare(queue=street_queue)


# 放入html队列
def html_put_in_queue(data):
    channel.queue_declare(queue=first_queue)
    channel.basic_publish(exchange='',
                          routing_key=first_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))


# 放入url队列
def url_put_in_queue(data):
    channel.queue_declare(queue=list_queue)
    channel.basic_publish(exchange='',
                          routing_key=list_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    city_name = body['city_name']
    street_url = body['street_url']
    street_name = body['street_name']
    region_name = body['region_name']
    pinyin = body['pinyin']
    kind_code = body['kind_code']
    logo = street_url.split('/')[-1]
    html = request_get(street_url, ip,connection)
    try:
        tree = etree.HTML(html.content.decode())
        # 判断是否小于50页
        page_list = tree.xpath('//a[@class="PageLink"]')
        # 抓取所有的街道的url和名字
        cooking_url_list = tree.xpath('//*[@id="classfy"]/a[@data-cat-id]')
        if not page_list:
            # 放入队列
            data1 = {
                'html': html.text,
                'city': [city_name, region_name, street_name],
                'kind_code': kind_code,
            }
            print('只有一页,url={}'.format(street_url))
            html_put_in_queue(data1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        if page_list[-1].text == '50':
            for cooking_obj in cooking_url_list:
                cooking_url = cooking_obj.attrib['href']
                data = {
                    'city_name': city_name,
                    'cooking_url': cooking_url,
                    'region_name': region_name,
                    'street_name': street_name,
                    'kind_code': kind_code,
                    'pinyin': pinyin}
                print(data)
                channel.queue_declare(queue=cooking_queue)
                channel.basic_publish(exchange='',
                                      routing_key=cooking_queue,
                                      body=json.dumps(data),
                                      properties=pika.BasicProperties(
                                          delivery_mode=2,  # make message persistent
                                      ))
        else:
            data1 = {
                'html': html.text,
                'city': [city_name, region_name, street_name],
                'kind_code': kind_code,
            }
            html_put_in_queue(data1)
            for i in range(2, int(page_list[-1].text) + 1):
                not_first_url = 'http://www.dianping.com/' + pinyin + '/' + kind_code + '/' + logo + 'p' + str(i)
                data2 = {
                    'url': not_first_url,
                    'city': [city_name, region_name, street_name],
                    'kind_code': kind_code,
                }
                print(data2)
                url_put_in_queue(data2)
    except Exception as e:
        channel.basic_publish(exchange='',
                              routing_key=street_queue,
                              body=json.dumps(body),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=street_queue, consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-dyn.abuyun.com", "port": "9020",
                                                         "user": "H51910O3VL7534QD", "pass": "42DE00B25FC5330C"}
    consume_start(ip)
