"""
每一个列表中含有100个字典
"""
import pika
import json
from pymongo import MongoClient
from lib.log import LogHandler
from backup.amap_road import adcode_list_other
import yaml
import itertools

setting = yaml.load(open('config_road.yaml'))
rabbit_mq_config = setting['rabbitmq']
log = LogHandler('other_city_producer')

rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_mq_config['host'], 5673))
channel = rabbit_connection.channel()
channel.queue_declare(queue=rabbit_mq_config['queue_name'])


def start_produce():
    client = MongoClient(host='114.80.150.196',
                         port=27777,
                         username='goojia',
                         password='goojia7102')

    db = client['amap']
    collections = db['max_street']
    for city_code in adcode_list_other:
        iter_all = []
        print(city_code)
        try:
            results = collections.find({'city_code': city_code}, no_cursor_timeout=True)
            for result in results:
                params_list = []
                numbers = result['number']
                city_code = result['city_code']
                street = result['street']
                region = result['region']
                city_name = result['city_name']
                for num in range(0, int(numbers) + 1):
                    params_dict = {'city_code': city_code,
                                   'number': str(num),
                                   'street': street,
                                   'region': region,
                                   'city_name': city_name}
                    params_list.append(params_dict)
                iter_all = itertools.chain(params_list, iter_all)

                small_list = []
                for params in iter_all:
                    small_list.append(params)
                    if len(small_list) == 100:
                        channel.basic_publish(
                            exchange='',
                            routing_key=rabbit_mq_config['queue_name'],
                            body=json.dumps(small_list)
                        )
                        print('将存有100个字典的列表放入到队列中')
                        small_list.clear()
        except:
            print('出现错误，不放入队列')