"""
    消费xiaozijia_num队列，请求，入小区库
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from xiaozijia.user_headers import get_headers
import requests
import yaml
import json

log = LogHandler('小资家_comm')

setting = yaml.load(open('config.yaml'))

# mongo
m = Mongo(setting['xiaozijia']['mongo']['host'], setting['xiaozijia']['mongo']['port'],
          # user_name=setting['xiaozijia']['mongo']['user_name'], password=setting['xiaozijia']['mongo']['password']
          )
coll_comm = m.connect[setting['xiaozijia']['mongo']['db']][setting['xiaozijia']['mongo']['comm_coll']]

# rabbit
r = Rabbit(setting['xiaozijia']['rabbit']['host'], setting['xiaozijia']['rabbit']['port'])
channel = r.get_channel()
queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_num']
build_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_build']
channel.queue_declare(queue=queue)
channel.queue_declare(queue=build_queue)


class Comm(object):
    def __init__(self, username):
        self.headers = get_headers(username)
        self.user_name = username

    def get_comm_info(self, ch, method, properties, body):
        """
        消费xiaozijia_num队列，请求，入小区库，并放入楼栋页
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        comm_url = 'http://www.xiaozijia.cn/ConstructionInfo/' + str(body.decode())
        try:
            response = requests.get(comm_url)
            html_json = response.json()
            ConstructionId = html_json['ConstructionId']
            is_ex = coll_comm.find_one({'ConstructionId': ConstructionId})
            if is_ex:
                log.info('小区存在，url="{}"'.format(comm_url))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            channel.basic_publish(exchange='',
                                  routing_key=build_queue,
                                  body=json.dumps(html_json))
            coll_comm.insert_one(html_json)
            log.info('插入一条小区数据,data={}'.format(html_json))
        except Exception as e:
            log.error('请求错误，url="{}"'.format(comm_url, e))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.get_comm_info, queue=queue)
        channel.start_consuming()


if __name__ == '__main__':
    pass
