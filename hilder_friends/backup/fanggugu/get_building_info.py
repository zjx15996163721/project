import requests
import json
from multiprocessing import Process
from fanggugu.login_fgg import Login
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit

# 连接rabbit mq
r = Rabbit('192.168.0.235', 5673)
channel = r.get_channel()
channel.queue_declare(queue='fgg_community_id')
channel.queue_declare(queue='fgg_building_id')

# 连接mongodb
m = Mongo('192.168.0.235', 27017)
connection = m.get_connection()
coll_insert = m.get_connection()['fgg']['fanggugu_building']
coll_login = m.get_connection()['fgg']['login']
coll_user = m.get_connection()['fgg']['user_info']


class GetBuild(object):
    def __init__(self):
        self.login = Login()

    def request_post(self, url, headers, city_name, ResidentialAreaID):
        params = {'city': city_name,
                  'id': ResidentialAreaID,
                  'type': 'xiaoqu'}
        while True:
            data = {"app_name": 'fgg'}
            ip = requests.post(url='http://192.168.0.235:8999/get_one_proxy', data=data).text
            print(ip)
            proxies = {'http': ip}
            try:
                result = requests.post(url=url, headers=headers, params=params,
                                       proxies=proxies, timeout=5)
                print(result.text)
                # 登录失效，重新登录
                if 'login' in result.text:
                    jrbqiantai = self.login.update_mongo(user_name)
                    headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
                    result = requests.post(url=url, headers=headers, params=params,
                                           proxies=proxies, timeout=5)
                if 'true' in result.text or 'True' in result.text:
                    print('ip can use')
                    return result
                else:
                    formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                    response = requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=formdata)
                    status = response.text
                    print(status)

            except Exception as e:
                formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                response = requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=formdata)
                status = response.text
                print(status)

    def start_building_info(self, ch, method, properties, body):
        user_name = method.consumer_tag
        jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
        headers = {
            'Cookie': 'jrbqiantai=' + jrbqiantai,
            'Referer': 'http://www.fungugu.com/JinRongGuZhi/toJinRongGuZhi_s?xqmc=DongHuVillas&gjdx=DongHuVillas&residentialName=&realName=&dz=&xzq=%E9%95%BF%E5%AE%81%E5%8C%BA&xqid=22013&ldid=&dyid=&hid=&loudong=&danyuan=&hu=&retrievalMethod=%E6%99%AE%E9%80%9A%E6%A3%80%E7%B4%A2',
            'User-Agent': "Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
        }
        message = json.loads(body.decode())
        ResidentialAreaID = message['ResidentialAreaID']
        city_name = message['city_name']
        url = 'http://www.fungugu.com/JinRongGuZhi/getLiandong'
        try:
            result = self.request_post(url, headers, city_name, ResidentialAreaID)
            building_list = json.loads(result.text)['list']
            if not building_list:
                print('没有building信息 - - None')
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            for i in building_list:
                building_id = i['id']
                building_name = i['name']
                building_type = i['type']
                data = {
                    'building_id': building_id,
                    'building_name': building_name,
                    'building_type': building_type,
                    'city': city_name,
                    'ResidentialAreaID': ResidentialAreaID,
                }
                print(data)
                channel.basic_publish(exchange='',
                                      routing_key='fgg_building_id',
                                      body=json.dumps(data),
                                      )
                coll_insert.insert_one(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)
            channel.basic_publish(exchange='',
                                  routing_key='fgg_community_id',
                                  body=body,
                                  )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self, name):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.start_building_info, queue='fgg_community_id',
                              consumer_tag=name)
        channel.start_consuming()


if __name__ == '__main__':
    count = 0
    build = GetBuild()
    for i in coll_user.find():
        user_name = i['user_name']
        print(user_name)
        build.consume_queue(user_name)
