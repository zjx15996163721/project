import pika
import uuid
import yaml
import json
from pymongo import MongoClient
from dianping.shop_detail import ShopDetail
import datetime

setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]


class ConvertIdRpcClient(object):
    def __init__(self, proxies):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)
        self.proxies = proxies

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, body):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id),
                                   body=json.dumps(body))
        while self.response is None:
            self.connection.process_data_events()
        if dianping_all_type_collection.find_one({"id": json.loads(self.response.decode())['id']}) is None:
            # todo 连同经纬度一起入库
            shop_detail = ShopDetail(self.proxies)
            info, lat, lng = shop_detail.async_message(json.loads(self.response.decode())['id'])
            json.loads(self.response.decode()).update({'crawler_time': datetime.datetime.now(), 'info': info, 'lat': lat, 'lng': lng})
            dianping_all_type_collection.insert_one(json.loads(self.response.decode()))
            print('插入一条数据 {}'.format(json.loads(self.response.decode())))
        else:
            # todo 更新数据, 连同经纬度一起入库
            print("库中已经存在")
            shop_detail = ShopDetail(self.proxies)
            info, lat, lng = shop_detail.async_message(json.loads(self.response.decode())['id'])
            json.loads(self.response.decode()).update({'update_time': datetime.datetime.now(), 'info': info, 'lat': lat, 'lng': lng})
            dianping_all_type_collection.find_one_and_replace({"id": json.loads(self.response.decode())['id']}, json.loads(self.response.decode()))
            print('更新一条数据 {}'.format(json.loads(self.response.decode())))


if __name__ == '__main__':
    convert_id_rpc_client = ConvertIdRpcClient(proxies='')
    print("开始请求")
    body = {
        'name': '宜宾燃面',
        'matchText': '高新西区  粉面馆',
        'cityId': '1610'
    }
    convert_id_rpc_client.call(body)










