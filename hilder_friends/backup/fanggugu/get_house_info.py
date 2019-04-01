import requests
import time
import json
from multiprocessing import Process
from fanggugu.login_fgg import Login
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit

# 连接mongodb
m = Mongo('192.168.0.235', 27017)
connection = m.get_connection()
coll_insert = m.get_connection()['fgg']['fanggugu_house']
coll_login = m.get_connection()['fgg']['login']
coll_user = m.get_connection()['fgg']['user_info']

# 连接rabbit mq
r = Rabbit('192.168.0.235', 5673)
channel = r.get_channel()
channel.queue_declare(queue='fgg_building_id')


class GetHouse(object):
    def __init__(self):
        self.login = Login()

    def start_house_info(self, ch, method, properties, body):
        user_name = method.consumer_tag
        jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
        headers = {
            'Cookie': 'jrbqiantai=' + jrbqiantai,
            'Referer': 'http://www.fungugu.com/JinRongGuZhi/toJinRongGuZhi_s?xqmc=DongHuVillas&gjdx=DongHuVillas&residentialName=&realName=&dz=&xzq=%E9%95%BF%E5%AE%81%E5%8C%BA&xqid=22013&ldid=&dyid=&hid=&loudong=&danyuan=&hu=&retrievalMethod=%E6%99%AE%E9%80%9A%E6%A3%80%E7%B4%A2',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        }
        message = json.loads(body.decode())
        ResidentialAreaID = message['ResidentialAreaID']
        city_name = message['city']
        building_id = message['building_id']
        url = 'http://www.fungugu.com/JinRongGuZhi/getLiandong'
        params = {
            'city': city_name,
            'id': building_id,
            'type': 'danyuan'
        }
        try:
            while True:
                # 获取ip

                data = {"app_name": 'fgg'}
                try:
                    ip = requests.post(url='http://192.168.0.235:8999/get_one_proxy', data=data).text
                    proxies = {'http': ip}
                    print(ip)
                except Exception as e:
                    print(e)
                try:
                    response = requests.post(url=url, headers=headers, params=params,
                                             proxies=proxies, timeout=5)
                    print(response.text)
                    # 登录失效，重新登录
                    if 'login' in response.text:
                        jrbqiantai = self.login.update_mongo(user_name)
                        headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
                        response = requests.post(url=url, headers=headers, params=params,
                                                 proxies=proxies, timeout=5)
                        print(response.text)
                    break
                except Exception as e:
                    formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                    response = requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=formdata)
                    status = response.text
                    print('更新' + status)

            if 'true' or 'True' in response.text:
                house_list = json.loads(response.text)['list']
                if not house_list:
                    print('没有house信息 - - None')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                for i in house_list:
                    house_id = i['id']
                    house_name = i['name']
                    house_type = i['type']
                    data = {
                        'house_id': house_id,
                        'house_name': house_name,
                        'ResidentialAreaID': ResidentialAreaID,
                        'city_name': city_name,
                        'house_type': house_type,
                        'building_id': building_id,
                    }
                    print(data)
                    coll_insert.insert_one(data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                channel.basic_publish(exchange='',
                                      routing_key='fgg_building_id',
                                      body=body,
                                      )
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)
            channel.basic_publish(exchange='',
                                  routing_key='fgg_building_id',
                                  body=body,
                                  )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self, user_name):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.start_house_info, queue='fgg_building_id',
                              consumer_tag=user_name)
        channel.start_consuming()


if __name__ == '__main__':
    house = GetHouse()
    for i in coll_user.find():
        user_name = i['user_name']
        house.consume_queue(user_name)
