"""
爬取顺序：城市-区域-街道-菜系
start:7
"""

import json
import yaml
from lxml import etree
from lib.rabbitmq import Rabbit
from lib.mongo import Mongo
import re

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection
channel = connection.channel()
all_url_queue = setting['dianping']['rabbit']['queue']['all_url_queue']
first_queue = setting['dianping']['rabbit']['queue']['first_queue']
channel.queue_declare(queue=all_url_queue)
channel.queue_declare(queue=first_queue)

# MongoDB
m = Mongo(setting['dianping']['mongo']['host'], setting['dianping']['mongo']['port'])
coll = m.connect[setting['dianping']['mongo']['db']][setting['dianping']['mongo']['save_coll']]


def callback(ch, method, properties, body):
    body = json.loads(body.decode())
    html = body['html']
    kind_code = body['kind_code']
    if not html:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    city = body['city']
    tree = etree.HTML(html)
    try:
        info_list = tree.xpath('//*[@id="shop-all-list"]/ul/li/div[2]')
        for info in info_list:
            url = info.xpath('div/a[@data-hippo-type="shop"]/@href')[0]
            shop_info = info.xpath('string()').encode().decode()
            shop_id = re.search('shop/(.*?)$', url).group(1)
            is_ex = coll.find_one({'shop_id': shop_id})
            if is_ex:
                continue
            data = {'city': city, 'url': url, 'shop_id': shop_id, 'kind_code': kind_code, 'info': shop_info}
            print(data)
            channel.basic_publish(exchange='',
                                  routing_key=all_url_queue,
                                  body=json.dumps(data),
                                  )
    except Exception as e:
        print(e)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=first_queue)
    channel.start_consuming()


if __name__ == '__main__':
    consume_start()
