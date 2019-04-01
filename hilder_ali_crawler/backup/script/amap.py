"""
根据小区名称 和 城市找到 小区地址
"""
import requests
from lib.proxy_iterator import Proxies
from lib.mongo import Mongo
import pika
import json
from multiprocessing import Process

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
collection = m.connect['amap']['amap_road_clean']

p = Proxies()
proxies = p.get_one()

city_code = {'绍兴': '330600',
             '烟台': '370600',
             '湖州': '330500',
             '枣庄': '370400',
             '丽水': '331100',
             '金华': '330700',
             '衢州': '330800',
             '临沂': '371300',
             '舟山': '330900',
             '莱芜': '371200',
             '威海': '371000',
             '青岛': '370200',
             '嘉兴': '330400',
             '温州': '330300',
             '台州': '331000',
             '杭州': '330100',
             '济宁': '370800',
             '菏泽': '371700',
             '泰安': '370900',
             '宁波': '330200',
             '聊城': '371500',
             '日照': '371100',
             '德州': '371400',
             '济南': '370100',
             '潍坊': '370700',
             '滨州': '371600',
             '东营': '370500',
             '淄博': '370300'}

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))


def check():
    l = []
    for i in collection.find():
        try:
            if i['amap_json']['status'] is not '1':
                print(i['id'])
                l.append(i['id'])
        except:
            print(i['id'])
            l.append(i['id'])
    print(l)

class Producer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5673))

    def produce(self):
        channel = self.connection.channel()
        channel.queue_declare(queue='amap_tmp')
        l = [16065]
        for i in l:
            info = collection.find_one({'id':i})
            # for i in collection.find():
            del info['_id']
            channel.basic_publish(exchange='',
                                  routing_key='amap_tmp',
                                  body=json.dumps(info))
            print(" [x] Sent 'Hello World!'")


class Amap:
    def __init__(self, proxies):
        self.url = 'https://www.amap.com/service/poiInfo?'
        self.proxies = proxies

    def start_consumer(self):
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='amap_tmp', )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        city = body['city']
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
            'city': city_code[city],
            'keywords': body['name'],
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
        collection.update({'id': body['id']},
                          {"$set": {'amap_json': res.json()}})
        print(res.text, body['id'])
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    # p = Producer()
    # p.produce()
    s = set()
    for i in collection.find():
        s.add(i['name'])
    print(len(s))
    # for i in range(6):
    #     a = Amap(next(p))
    #     Process(target=a.start_consumer).start()
    # a = Amap(proxies)
    # a.start_consumer()
