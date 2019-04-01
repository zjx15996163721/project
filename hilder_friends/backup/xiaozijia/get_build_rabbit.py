"""
    消费xiaozijia_build队列，请求，入楼栋库xiaozijia_build_fast
    大约需要10个小时
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import requests
import json
import yaml
from xiaozijia.user_headers import get_headers

log = LogHandler('小资家_build')

setting = yaml.load(open('config.yaml'))

# mongo
m = Mongo(setting['xiaozijia']['mongo']['host'], setting['xiaozijia']['mongo']['port'],
          user_name=setting['xiaozijia']['mongo']['user_name'], password=setting['xiaozijia']['mongo']['password'])
coll_build = m.connect[setting['xiaozijia']['mongo']['db']][setting['xiaozijia']['mongo']['build_coll']]

# rabbit
r = Rabbit(setting['xiaozijia']['rabbit']['host'], setting['xiaozijia']['rabbit']['port'])
channel = r.get_channel()
build_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_build']
house_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_house']
channel.queue_declare(queue=build_queue)
channel.queue_declare(queue=house_queue)


class Build(object):
    def __init__(self, username):
        self.headers = get_headers(username)
        self.user_name = username

    def get_build_info(self, ch, method, properties, body):
        """
        消费xiaozijia_build队列，请求，入小区库，并放入房号页
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        body_json = json.loads(body.decode())
        ConstructionPhaseId = body_json['ConstructionPhaseId']
        ConstructionName = body_json['ConstructionName']
        ConstructionId = body_json['ConstructionId']
        build_url = 'http://www.xiaozijia.cn/HousesForJson/' + ConstructionPhaseId + '/2'
        try:
            response = requests.get(build_url, headers=self.headers, timeout=20)
            html_json = response.json()
            if not html_json:
                log.info('小区没有楼栋，url={}'.format(build_url))
            for i in html_json:
                i['ConstructionName'] = ConstructionName
                i['ConstructionId'] = ConstructionId
                channel.basic_publish(exchange='',
                                      routing_key=house_queue,
                                      body=json.dumps(i))
                coll_build.insert_one(i)
                log.info(i)

        except Exception as e:
            self.headers = get_headers(self.user_name)
            log.error('请求错误，url="{}",ConstructionPhaseId="{}",ConstructionName="{}",ConstructionId="{}",e="{}"'
                      .format(build_url, ConstructionPhaseId, ConstructionName, ConstructionId, e))
            channel.basic_publish(exchange='',
                                  routing_key=build_queue,
                                  body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.get_build_info, queue=build_queue)
        channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
