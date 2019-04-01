import requests
import pymongo
import time
import pika
import json
import random
from multiprocessing import Process

ips = [
    "192.168.0.90:4234",
    "192.168.0.93:4234",
    "192.168.0.94:4234",
    "192.168.0.96:4234",
    "192.168.0.98:4234",
    "192.168.0.99:4234",
    "192.168.0.100:4234",
    "192.168.0.101:4234",
    "192.168.0.102:4234",
    "192.168.0.103:4234"
]


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port, connect=False)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, ))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


def login(ip, user_id):
    s = requests.session()
    parms = {'pwd_login_username': user_id,
             'pwd_login_password': '4ac9fa21a775e4239e4c72317cdca870',
             'remembermeVal': 0}
    proxies = {
        'http': ip
    }
    s.get(url='http://www.fungugu.com/DengLu/doLogin_noLogin', params=parms,
          proxies=proxies)
    jrbqiantai = s.cookies.get_dict()['jrbqiantai']
    return jrbqiantai


channel = connect_rabbit('192.168.0.235', 'fgg_area_id')
fgg_coll = connect_mongodb('192.168.0.235', 27017, 'fgg', 'fanggugu_price')


class get_name(object):
    def __init__(self, ip):
        self.ip = ip

    def put_area_id(self):
        for i in fgg_coll.find():
            residentialAreaId = i['ResidentialAreaID']
            city_name = i['city_name']
            data = {
                'residentialAreaId': residentialAreaId,
                'city_name': city_name,
            }
            print(data)
            channel.basic_publish(exchange='',
                                  routing_key='fgg_area_id',
                                  body=json.dumps(data),
                                  )

    def callback(self,ch, method, properties, body):
        cookie_ = method.consumer_tag
        area_id = body.decode()
        data = json.loads(area_id)
        residentialAreaId = data['residentialAreaId']
        city_name = data['city_name']
        params = {
            'residentialAreaId': residentialAreaId,
            'city': city_name,
        }
        print(params)
        proxies = {
            'http': self.ip
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36',
            'Cookie': 'jrbqiantai=' + cookie_,
        }
        url = 'http://www.fungugu.com/JinRongGuZhi/getBaseinfo'
        time.sleep(5)
        try:
            response = requests.post(url=url, headers=headers, params=params, proxies=proxies)
            print(response.text)
            if 'true' in response.text:
                baseinfo = response.json()
                fgg_coll.update({'ResidentialAreaID': residentialAreaId, 'city_name': city_name},
                                {'$set': {'baseinfo': baseinfo}})
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print('False:已放队列')
                channel.basic_publish(exchange='',
                                      routing_key='fgg_area_id',
                                      body=body,
                                      )
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)
            channel.basic_publish(exchange='',
                                  routing_key='fgg_area_id',
                                  body=body,
                                  )
            ch.basic_ack(delivery_tag=method.delivery_tag)
    def consume_queue(self,cookie):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.callback, queue='fgg_area_id', consumer_tag=cookie)
        channel.start_consuming()


if __name__ == '__main__':
    coll = connect_mongodb('192.168.0.235', 27017, 'fgg', 'user_info').find({})
    for i in coll:
        user_id = i['user_name']
        ip = random.choice(ips)
        cookie = login(ip, user_id)
        name = get_name(ip)
        Process(target=name.consume_queue, args=(cookie,)).start()
