import pymysql
import pika
import requests
import re
import gevent
import json
from pymongo import MongoClient
from backup.amap_road.city_code import city_code_dict
from gevent import monkey
from lib.log import LogHandler

log = LogHandler("road")

monkey.patch_all()
connection = pymysql.connect(host='114.80.150.197',
                             port=3336,
                             user='root',
                             password='fangjia123456',
                             db='data_quality')
cursor = connection.cursor()
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')

# max_street_collection = m['amap']['max_street']
max_street_collection = m['amap']['test_street']


class Producer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))

    def produce(self):
        channel = self.connection.channel()
        channel.queue_declare(queue='amap_tmp')
        cursor.execute("SELECT * FROM data_quality.poi_roadnew")
        street_list = []
        for i in cursor.fetchall():
            city_len = len(i[1])
            #此处将区域减去city存入到队列中
            street_list.append({'city': i[1], 'region':i[2][city_len:], 'street': i[3]})
            if len(street_list) == 100:
                channel.basic_publish(exchange='',
                                      routing_key='amap_tmp',
                                      body=json.dumps(street_list))
                print(" [x] Sent 'Hello World!'")
                street_list.clear()

    def produce_log(self):
        channel = self.connection.channel()
        channel.queue_declare(queue='amap_tmp')
        with open('error_road.txt', 'rb') as f:
            lines = f.readlines()
            street_list = []
            for line in lines:
                print(line.decode('utf-8'))
                result = re.search('ERROR city=(.*?), keywords=(.*?)10000号', line.decode('utf-8'), re.S | re.M)
                city = result.group(1)
                keywords = result.group(2)
                street_list.append({'city': city, 'street': keywords})
                if len(street_list) == 100:
                    channel.basic_publish(exchange='',
                                          routing_key='amap_tmp',
                                          body=json.dumps(street_list))
                    print(" [x] Sent 'Hello World!'")
                    street_list.clear()


class Amap:
    def __init__(self, proxies):
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.proxies = proxies

    def start_consumer(self):
        channel = rabbit_connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='amap_tmp',
                              )
        channel.start_consuming()

    def async_message(self, info):
        city = info['city']
        city_code = city_code_dict[city]
        # city_code = info['city']
        street = info['street']
        #添加region
        region = info['region']
        body_long = region + street + '10000号'
        payload = {
            'query_type': 'TQUERY',
            'pagesize': '20',
            'pagenum': '1',
            'qii': 'true',
            'cluster_state': '5',
            'need_utd': 'true',
            'utd_sceneid': '1000',
            'div': 'PC1000',
            'addr_poi_merge': 'true',
            'is_classify': 'true',
            'city': city_code,
            'keywords': body_long,
        }
        try:
            res = requests.get(self.url, proxies=self.proxies, params=payload)
        except Exception as e:
            print('网络请求失败')
            log.error('city={}, keywords={}'.format(city_code, body_long))
            return
        try:
            address = res.json()['data']['poi_list'][0]['address']
            number = re.search(street + '(\d+)号', address, re.S | re.M).group(1)
        except Exception as e:
            print('本条匹配不到道路')
            return
        max_street_collection.insert_one({
            'city_code': city_code,
            'number': number,
            'street': street,
            'region': region,
            'city_name':city
        })
        print({
            'city_code': city_code,
            'number': number,
            'street': street,
            'region':region,
            'city_name':city
        })

    def callback(self, ch, method, properties, body):
        jobs = [gevent.spawn(self.async_message, info) for info in json.loads(body.decode())]
        gevent.wait(jobs)
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    p = Producer()
    # p.produce_log()
    p.produce()
    # proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
    #     "host": "http-proxy-sg2.dobel.cn",
    #     "port": "9180",
    #     "account": 'FANGJIAHTT8',
    #     "password": "HGhyd7BF",
    # }
    # proxies = {"https": proxy,
    #            "http": proxy}
    # c = Amap(proxies)
    # c.start_consumer()
