from multiprocessing import Process, Pool
import json
import pika
import requests
import random
import gevent
import time
from gevent import monkey
pool_list = []



class HouseId(object):
    # 建立实例，声明管道，声明队列
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='192.168.0.190', port=5673))
    channel = connection.channel()
    channel.queue_declare(queue='yfsd_building')

    # 设置请求头
    headers = {
        'Origin': "https://yfsdtay.cmbc.com.cn",
        'User-Agent': "Mozilla/5.0 (Linux; Android 7.0; SM-C7010 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044028 Mobile Safari/537.36 MicroMessenger/6.6.5.1280(0x26060536) NetType/WIFI Language/zh_CN",
        'Referer': "https://yfsdtay.cmbc.com.cn/wxp/yfsd/page/houseMsg.html",
        'Cookie': "JSESSIONID=A9581AEC64DDD758EEAB65ADDACC46E7; BIGipServerdlwgBJset__zifushuiEtong_443_pool=3830644746.20480.0000; BIGipServerdlwgGuangZWX_gzwxzhicheng_80_pool=3813867530.20480.0000",
        'X-Requested-With': 'XMLHttpRequest'
    }

    def callback(self, ch, method, properties, body):
        body_dict = json.loads(body.decode())
        # 获取队列中的数据
        if 'city' in body_dict:
            city_url = body_dict['city_url']
            buildingId = body_dict['buildingId']
            print(city_url)
            print(buildingId)
            city = body_dict['city']
            # 发起第三次请求，得到房间的Id
            try:
                a = time.asctime()
                code = '?t=Thu%20May%2003%202018%20' + a.split()[
                    3] + '%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
                response = requests.post(
                    city_url + '/wxp/yfsd/loadHouseData' + code,
                    data={'buildingId': str(buildingId)},
                    headers=self.headers,
                )
                result = json.loads(response.content.decode('utf-8'))
                if 'resultData' in result:
                    data = {
                        'resultData': result['resultData'],
                        'city': city,
                    }
                    self.channel.queue_declare(queue='yfsd_house')
                    self.channel.basic_publish(exchange='',
                                               routing_key='yfsd_house',
                                               body=json.dumps(data)
                                               )
                    print("==" * random.randint(1, 20))
                else:
                    print("NO RESULT:", result)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self.channel.queue_declare(queue='yfsd_building')
                self.channel.basic_publish(exchange='',
                                           routing_key='yfsd_building',
                                           body=body
                                           )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(e, buildingId)
        else:
            self.channel.queue_declare(queue='yfsd_building')
            self.channel.basic_publish(exchange='',
                                       routing_key='yfsd_building',
                                       body=body
                                       )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                                   queue='yfsd_building')
        self.channel.start_consuming()


def asynchronous():
    worker = HouseId()
    monkey.patch_all()
    threads = [gevent.spawn(worker.consume_start) for i in range(20)]
    gevent.joinall(threads)


if __name__ == '__main__':
    # asynchronous()
    worker = HouseId()
    # gevent_list = []
    # for i in range(50):
    #     g = gevent.spawn(worker.consume_start)
    #     gevent_list.append(g)
    # gevent.joinall(gevent_list)
    from threading import Thread
    for i in range(30):
        Process(target=worker.consume_start).start()