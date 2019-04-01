"""
城市房价评估
"""
import requests
from pymongo import MongoClient
import time
import pika
from lib.proxy_iterator import Proxies
import datetime

p = Proxies()
l_m = MongoClient('114.80.150.196', 27777,username='goojia',password='goojia7102')
result_collection = l_m['friends']['viss']
viss_no_find_project_name = l_m['friends']['viss_no_find_project_name']

rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))


# class Producer:
#     @staticmethod
#     def produce():
#         channel = rabbit_connection.channel()
#         channel.queue_declare(queue='amap_tmp', durable=True)
#         for i in viss_no_find_project_name.find(no_cursor_timeout=True):
#             ProjectName = i['ProjectName']
#             name = ProjectName[0:3.png]
#             channel.basic_publish(exchange='',
#                                   routing_key='amap_tmp',
#                                   body=name,
#                                   properties=pika.BasicProperties(delivery_mode=2, )
#                                   )
#             print("添加到队列 name={}".format(name))


class Viss:
    def __init__(self, open_id):
        self.open_id = open_id

    def start_consumer(self):
        channel = rabbit_connection.channel()
        channel.queue_declare(queue='amap_tmp', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='amap_tmp', )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        headers = {
            'Cookie': self.open_id,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044205 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x26070233) NetType/WIFI Language/zh_CN'
        }
        payload = {'district': '0',
                   'plate': '0',
                   'address': body.decode('utf-8').strip(),
                   'isSchool': 'false',
                   'projectType': '0',
                   'completionYearFrom': 'null',
                   'completionYearTo': 'null',
                   'webpage': '1',
                   'sortColumn': '1',
                   'sort': 'true', }
        url = 'http://wx.surea.com/api/Viss/GetProjectList?'
        r = requests.get(url=url, params=payload, headers=headers)
        if r.json()["ErrorCode"] != "000000":
            print(r.json())
            print(1/0)
        print(r.text)
        print(self.open_id)
        if len(r.json()['List']) == 0:
            print('数据为空')
        else:
            for info in r.json()['List']:
                try:
                    info.update({'crawler_time': datetime.datetime.now()})
                    result_collection.insert_one(info)
                except:
                    print('重复数据')
        rabbit_connection.process_data_events()
        time.sleep(20)
        rabbit_connection.process_data_events()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def detail(self):
        url = 'http://wx.surea.com/api/Viss/GetProjectInfo?projectId=989da6d7-2683-41e2-9cd9-2f9a82758d7d'


if __name__ == '__main__':
    # s = Producer()
    # s.produce()
    l = ['ASP.NET_SessionId=entewvkyhomv3pghfogoh30e',
         ]
    for i in l:
        v = Viss(open_id=i)
        v.start_consumer()
