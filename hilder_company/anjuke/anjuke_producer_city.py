"""
将安居客上所有的城市列表放入到队列中，，，方便请求获取楼盘详情页链接
"""
import pika
import json
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
from anjuke.analyse_city import can_not_stan_city,city_list
log = LogHandler('anjuke_producer_city')

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1',
    port=5673,
    heartbeat=0
))
channel = connection.channel()
channel.queue_declare(queue='no_anjuke_city_url_list', durable=True)
p = Proxies()
def analyse_city():
    for city_dict in can_not_stan_city:
        city_url = city_dict.values()
        for url in city_url:
            channel.basic_publish(
                exchange='',
                routing_key='no_anjuke_city_url_list',
                body=json.dumps(url),
                properties=pika.BasicProperties(delivery_mode=2)
            )


if __name__ == '__main__':
    analyse_city()
