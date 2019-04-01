"""
爬取顺序：城市-区域-街道-菜系
start:2
"""

from lxml import etree
import json
import yaml
import pika
from lib.rabbitmq import Rabbit
from dianping.request_detail import request_get

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
city_queue = setting['dianping']['rabbit']['queue']['city_queue']
first_queue = setting['dianping']['rabbit']['queue']['first_queue']
list_queue = setting['dianping']['rabbit']['queue']['list_queue']
region_queue = setting['dianping']['rabbit']['queue']['region_queue']
channel.queue_declare(queue=city_queue)


# 放入html队列
def html_put_in_queue(data):
    channel.queue_declare(queue=first_queue)
    channel.basic_publish(exchange='',
                          routing_key=first_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          )
                          )


# 放入url队列
def url_put_in_queue(data):
    channel.queue_declare(queue=list_queue)
    channel.basic_publish(exchange='',
                          routing_key=list_queue,
                          body=json.dumps(data),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          )
                          )


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    city_name = body['city_name']
    pinyin = body['pinyin']
    kind_code = body['kind_code']
    url = 'http://www.dianping.com/' + pinyin + '/' + kind_code
    response = request_get(url, ip,connection)
    try:
        tree = etree.HTML(response.text)
        # 抓取所有的行政区的url和名字
        if kind_code == 'ch90':
            page_list = tree.xpath('//a[@class="pageLink"]')
            region_url_list = tree.xpath('//a[@data-click-bid="b_4wybqh04"]')
        else:
            page_list = tree.xpath('//a[@class="PageLink"]')
            region_url_list = tree.xpath('//*[@id="region-nav"]/a[@data-cat-id]')
        if not page_list:
            # 放入队列
            data1 = {
                'html': response.text,
                'city': [city_name],
                'kind_code': kind_code,
            }
            html_put_in_queue(data1)
            print('只有一页')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 判断是否小于50页
        if page_list[-1].text == '50':
            for region_obj in region_url_list:

                if kind_code == 'ch90':
                    region_name = region_obj.xpath('text()')[0]
                    region_url = 'http:' + region_obj.attrib['href']
                else:
                    region_name = region_obj.xpath('span')[0].text
                    region_url = region_obj.attrib['href']
                data = {
                    'city_name': city_name,
                    'region_url': region_url,
                    'region_name': region_name,
                    'pinyin': pinyin,
                    'kind_code': kind_code
                }
                print(data)
                channel.queue_declare(queue=region_queue)
                channel.basic_publish(exchange='',
                                      routing_key=region_queue,
                                      body=json.dumps(data),
                                      properties=pika.BasicProperties(
                                          delivery_mode=2,
                                      ))
        else:
            data1 = {
                'html': response.content.decode(),
                'city': [city_name],
                'kind_code': kind_code,
            }
            html_put_in_queue(data1)
            print('放入一个html页面')
            for i in range(2, int(page_list[-1].text) + 1):
                not_first_url = 'http://www.dianping.com/' + pinyin + '/' + kind_code + '/p' + str(i)
                data2 = {
                    'url': not_first_url,
                    'city': [city_name],
                    'kind_code': kind_code,
                }
                url_put_in_queue(data2)
                print('放入第%s个url' % (i - 1))
    except Exception as e:
        channel.basic_publish(exchange='',
                              routing_key=city_queue,
                              body=json.dumps(body),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,
                              ))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=city_queue, consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-dyn.abuyun.com", "port": "9020",
                                                         "user": "H51910O3VL7534QD", "pass": "42DE00B25FC5330C"}
    consume_start(ip)
