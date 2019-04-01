"""
爬取顺序：城市-区域-街道-菜系
start:6
"""

from dianping.request_detail import request_get
import json
import yaml
import pymongo
from lib.rabbitmq import Rabbit

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
first_queue = setting['dianping']['rabbit']['queue']['first_queue']
list_queue = setting['dianping']['rabbit']['queue']['list_queue']
channel.queue_declare(queue=list_queue)


def pinyin():
    client = pymongo.MongoClient(setting['dianping']['mongo']['host'], setting['dianping']['mongo']['port'])
    db = client[setting['dianping']['mongo']['db']]
    coll = db.get_collection(setting['dianping']['mongo']['url_list'])
    client.close()
    return coll


def get_logo(cooking_url):
    logo = cooking_url.split('/')[-1]
    return logo


# 放入html队列
def html_put_in_queue(data):
    channel.queue_declare(queue=first_queue)
    channel.basic_publish(exchange='',
                          routing_key=first_queue,
                          body=json.dumps(data),
                          )


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    url = body['url']
    city = body['city']
    kind_code = body['kind_code']
    response = request_get(url, ip,connection)
    try:

        data1 = {'html': response.text,
                 'kind_code': kind_code,
                 'city': city}
        print('放入队列，URL={}'.format(url))
        html_put_in_queue(data1)
        response.close()
    except Exception as e:
        channel.basic_publish(exchange='',
                              routing_key=list_queue,
                              body=json.dumps(body),
                              )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=list_queue, consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-dyn.abuyun.com", "port": "9020",
                                                         "user": "H51910O3VL7534QD", "pass": "42DE00B25FC5330C"}
    consume_start(ip)
