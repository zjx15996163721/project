import pika
import json
import yaml
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from lib.log import LogHandler

setting = yaml.load(open('config_amap.yaml'))
rabbit_setting = setting['amap']['rabbitmq']
mongo_setting = setting['amap']['mongo']
log = LogHandler(__name__)

client = MongoClient(host=mongo_setting['host'],
                     port=mongo_setting['port'],
                     username=mongo_setting['user_name'],
                     password=mongo_setting['password'])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_setting['host'], port=rabbit_setting['port'],heartbeat=0))
rabbit = connection.channel()
rabbit.queue_declare(queue='amap_result_json')
collection = client[mongo_setting['db']][mongo_setting['collection']]

collection.create_index('id', unique=True, name='id_index')
collection.create_index('typecode', name='type_code_index')
collection.create_index('cityname', name='city_name_index')


class ConsumeResult:
    @staticmethod
    def callback(ch, method, properties, body):
        json_result = json.loads(body.decode())
        pois = json_result.get('pois')
        if len(pois) > 0:
            try:
                collection.insert_many(pois, ordered=False)
            except BulkWriteError as e:
                log.error('{}该数据已经存在'.format(json_result))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_result(self):
        rabbit.basic_qos(prefetch_count=1)
        rabbit.basic_consume(self.callback,
                             queue='amap_result_json',
                             )
        rabbit.start_consuming()
