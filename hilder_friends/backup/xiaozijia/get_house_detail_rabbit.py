"""
    消费xiaozijia_house_detail队列，请求，入楼栋库xiaozijia_detail_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from xiaozijia.user_headers import get_headers
import requests
import json
import yaml

log = LogHandler('小资家_detail_fast')

setting = yaml.load(open('config.yaml'))

# mongo
m = Mongo(setting['xiaozijia']['mongo']['host'], setting['xiaozijia']['mongo']['port'],
          user_name=setting['xiaozijia']['mongo']['user_name'], password=setting['xiaozijia']['mongo']['password'])
coll_detail = m.connect[setting['xiaozijia']['mongo']['db']][setting['xiaozijia']['mongo']['detail_coll']]

# rabbit
r = Rabbit(setting['xiaozijia']['rabbit']['host'], setting['xiaozijia']['rabbit']['port'])
channel = r.get_channel()
detail_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_house_detail']
channel.queue_declare(queue=detail_queue)

headers = ''


def get_house_info(ch, method, properties, body):
    username = method.consumer_tag
    global headers
    headers = get_headers(username)
    body_json = json.loads(body.decode())
    ConstructionName = body_json['ConstructionName']
    BuildName = body_json['BuildName']
    Id = body_json['Id']
    detail_url = 'http://www.xiaozijia.cn/HouseInfo/' + str(Id)
    try:
        response = requests.get(detail_url, headers=headers, timeout=20)
        html_json = response.json()
        if not html_json.get('State'):
            log.error('请求错误，url="{}",BuildName="{}",ConstructionName="{}",Id="{}"'
                      .format(detail_url, BuildName, ConstructionName, Id))
            channel.basic_publish(exchange='',
                                  routing_key=detail_queue,
                                  body=body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        html_json['ConstructionName'] = ConstructionName
        html_json['BuildName'] = BuildName
        coll_detail.insert_one(html_json)
        log.info('插入一个数据，data="{}"'.format(html_json))

    except Exception as e:
        headers = get_headers(username)
        log.error('请求错误，url="{}",BuildName="{}",ConstructionName="{}",Id="{}",e="{}"'
                  .format(detail_url, BuildName, ConstructionName, Id, e))
        channel.basic_publish(exchange='',
                              routing_key=detail_queue,
                              body=body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue(username):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=get_house_info, queue=detail_queue, consumer_tag=username)
    channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
