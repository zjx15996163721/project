import pymysql
import pika
import requests
from lib.proxy_iterator import Proxies
import re
from multiprocessing import Process
from lib.mongo import Mongo
connection = pymysql.connect(host='114.80.150.197',
                             port=3336,
                             user='root',
                             password='fangjia123456',
                             db='data_quality')

cursor = connection.cursor()

client = Mongo(host='114.80.150.196',port=27777,user_name='goojia',password='goojia7102').connect
coll = client['amap']['amap_street']
coll.create_index([('street',1),('status',1)])


p = Proxies()
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))


class Producer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))

    def produce(self):
        channel = self.connection.channel()
        channel.queue_declare(queue='amap_tmp')
        cursor.execute("SELECT * FROM data_quality.poi_roadnew where city='上海'")
        for i in cursor.fetchall():
            channel.basic_publish(exchange='',
                                  routing_key='amap_tmp',
                                  body=i[3])
            print(" [x] Sent 'Hello World!'")


class Amap:
    def __init__(self, proxies):
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.proxies = proxies

    def start_consumer(self):
        channel = rabbit_connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='amap_tmp', )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        body_long = body.decode() + '10000号'
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
            'city': '310000',
            'keywords': body_long,
        }
        try:
            res = requests.get(self.url, proxies=self.proxies, params=payload)
        except:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        if res.json()['status'] is not '1':
            requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
            print('切换')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        try:
            address = res.json()['data']['poi_list'][0]['address']
        except:
            pass
        try:
            number = re.search(body.decode() + '(\d+)号', address, re.S | re.M).group(1)
            for i in range(1,int(number)+1):
                try:
                    coll.insert_one({'street':body.decode()+str(i)+'号','status':0})
                    print(body.decode()+str(i))
                except:
                    print("重复街道")
        except:
            pass
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    # p = Producer()
    # p.produce()
    for i in range(6):
        a = Amap(next(p))
        Process(target=a.start_consumer).start()
    # a = Amap(p.get_one())
    # a.start_consumer()
