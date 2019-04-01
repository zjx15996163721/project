import pika
import json
from pymongo import MongoClient
from lib.log import LogHandler
from backup.amap_road import adcode_list_other1
import yaml

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
    for city_code in adcode_list_other1:
        print(city_code)
        try:
            results = collections.find({'city_code': city_code}, no_cursor_timeout=True)
            for result in results:
                numbers = result['number']
                city_code = result['city_code']
                street = result['street']
                region = result['region']
                city_name = result['city_name']

                params_dict = {'city_code': city_code,
                               'number': numbers,
                               'street': street,
                               'region': region,
                               'city_name': city_name}
                channel.basic_publish(
                    exchange='',
                    routing_key=rabbit_mq_config['queue_name'],
                    body=json.dumps(params_dict)
                )
                print('将一个字典放入到队列中')
            print('{}放入队列结束'.format(city_code))
        except:
            print('出现错误，不放入队列')
