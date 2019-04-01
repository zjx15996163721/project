import pika
import json
import yaml
import requests
from pymongo import MongoClient
from lib.log import LogHandler
import datetime
from dianping.shop_detail import ShopDetail
from dianping.convert_id_rpc_client import ConvertIdRpcClient
s = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=s['mongo']['host'], port=s['mongo']['port'], username=s['mongo']['user_name'], password=s['mongo']['password'])
db = m[s['mongo']['db_name']]
shop_detail_collection = db[s['mongo']['shop_detail_collection']]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=s['rabbit']['host'], port=s['rabbit']['port']))
channel = connection.channel()
log = LogHandler(__name__)


class Consumer:
    def __init__(self, proxies):
        self.headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
                'Referer': 'https://m.dianping.com/'
            }
        self.proxies = proxies

    def start_consume(self):
        channel.queue_declare(queue='category_list_url')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.call_back,
                              queue='category_list_url',
                              no_ack=False)
        channel.start_consuming()

    def call_back(self, ch, method, properties, body):
        url = body.decode()
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            print(url)
            self.analyzer_insert(r)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)
            log.error('请求失败={}'.format(url))
            # 切换公网ip
            requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def analyzer_insert(self, r):
        """
        去重入库
        :param r: response object
        :return:
        """
        if '没有找到合适的商户' in r.text:
            print('没有找到合适的商户')
        else:
            try:
                json_body = json.loads(r.text)
                for i in json_body['list']:
                    if 'id' in i.keys():
                        if shop_detail_collection.find_one({"id": i['id']}, no_cursor_timeout=True) is None:
                            # todo 连同经纬度一起入库
                            shop_detail = ShopDetail(self.proxies)
                            info, lat, lng = shop_detail.async_message(i['id'])
                            i.update({'crawler_time': datetime.datetime.now(), 'info': info, 'lat': lat, 'lng': lng})
                            shop_detail_collection.insert(i)
                            print("插入一条数据 {}".format(i))


                            # i.update({'crawler_time': datetime.datetime.now()})
                            # shop_detail_collection.insert(i)
                            # print("插入一条数据 {}".format(i))
                            # # 将shop_id 放队列  shop_detail 抓经纬度时直接消费
                            # channel.queue_declare(queue='dianping_id_list')
                            # channel.basic_publish(exchange='',
                            #                       routing_key='dianping_id_list',
                            #                       body=json.dumps(i['id']))
                            # print("放队列 {}".format(i['id']))
                        else:
                            # todo 连同经纬度一起入库
                            print("已存在, 更新数据")
                            shop_detail = ShopDetail(self.proxies)
                            info, lat, lng = shop_detail.async_message(i['id'])
                            i.update({'update_time': datetime.datetime.now(), 'info': info, 'lat': lat, 'lng': lng})
                            shop_detail_collection.find_one_and_replace({"id": i['id']}, i)
                            print('更新一条数据 {}'.format(i))


                            # print("已存在, 更新数据")
                            # i.update({'update_time': datetime.datetime.now()})
                            # shop_detail_collection.find_one_and_replace({"id": i['id']}, i)
                            # print('更新一条数据 {}'.format(i))
                            # # 将shop_id 放队列  shop_detail 抓经纬度时直接消费
                            # channel.queue_declare(queue='dianping_id_list')
                            # channel.basic_publish(exchange='',
                            #                       routing_key='dianping_id_list',
                            #                       body=json.dumps(i['id']))
                            # print("放队列 {}".format(i['id']))
                    else:
                        # todo 连同经纬度一起入库
                        """
                        RPC调用,恢复没有ID的数据
                        """
                        convert_id_rpc_client = ConvertIdRpcClient(self.proxies)
                        print("RPC调用, 开始请求")
                        convert_id_rpc_client.call(i)

                        """
                        或者直接放队列
                        """
                        # channel.queue_declare(queue='dianping_no_id')
                        # channel.basic_publish(exchange='',
                        #                       routing_key='dianping_no_id',
                        #                       body=json.dumps(i))
                        # print("放队列 {}".format(i))
            except Exception as e:
                log.info('不能转为JSON格式 {}'.format(r.text))