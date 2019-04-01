"""
    实时的更新小区均价
"""

import json, time, requests, datetime

from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from login_fgg import Login
import random

# 链接 MongoDB
m = Mongo('192.168.0.235', 27017)

fgg = m.connect['fgg']
coll = fgg['fanggugu_price']

fgg = m.connect['fgg']
coll_test = fgg['fanggugu_price_update']

fgg = m.connect['fgg']
coll_user = fgg['user_info']

fgg = m.connect['fgg']
coll_login = fgg['login']

# 链接 rabbit
r = Rabbit('192.168.0.235', 5673, )

channel = r.get_channel()
channel.queue_declare(queue='fgg_comm_id')


# IPS = ["192.168.0.90:4234",
#        "192.168.0.93:4234",
#        "192.168.0.94:4234",
#        "192.168.0.96:4234",
#        "192.168.0.98:4234",
#        "192.168.0.99:4234",
#        "192.168.0.100:4234",
#        "192.168.0.101:4234",
#        "192.168.0.102:4234",
#        "192.168.0.103:4234"]


class Update_comm_price(object):
    def __init__(self):
        self.login = Login()

    def put_rabbit(self):
        # 从price表中查id和城市放入rabbit
        for i in coll.find():
            ResidentialAreaID = i['ResidentialAreaID']
            city_name = i['city_name']
            data = {
                'ResidentialAreaID': ResidentialAreaID,
                'city_name': city_name,
            }
            channel.basic_publish(exchange='',
                                  routing_key='fgg_comm_id',
                                  body=json.dumps(data))
            print(data)

    def request_post(self, url, headers, city_name, ResidentialAreaID, user_name):
        querystring = {
            'CityName': city_name,
            'ResidentialAreaID': ResidentialAreaID
        }
        while True:
            # 请求ip池
            data = {"app_name": 'fgg'}
            ip = requests.post(url='http://192.168.0.235:8999/get_one_proxy', data=data).text
            print(ip)
            # ip = random.choice(IPS)
            proxies = {'http': ip}
            try:
                result = requests.post(url=url, headers=headers, data=querystring,
                                       proxies=proxies, timeout=5)
                # 登录失效，重新登录
                if 'login' in result.text:
                    jrbqiantai = self.login.update_mongo(user_name)
                    headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
                    result = requests.post(url=url, headers=headers, data=querystring,
                                           proxies=proxies, timeout=5)
                if 'UnitPrice' in result.text:
                    print('ip can use')
                    return result
                else:
                    formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                    response = requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=formdata)
                    status = response.text
                    print('错误页面，更新', status)

            except Exception as e:
                formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                response = requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=formdata)
                status = response.text
                print('try，更新', status)

    def start_community_info(self, ch, method, properties, body):
        user_name = method.consumer_tag
        jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
        headers = {
            'Cookie': 'jrbqiantai=' + jrbqiantai,
            'Referer': 'http://www.fungugu.com/',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        }
        body_dict = json.loads(body.decode())
        city_name = body_dict['city_name']
        ResidentialAreaID = body_dict['ResidentialAreaID']
        print(city_name, ResidentialAreaID)
        try:
            url = 'http://www.fungugu.com/JinRongGuZhi/getXiaoQuJiChuXinXi'
            response = self.request_post(url, headers, city_name, ResidentialAreaID, user_name)
            data = json.loads(response.text)
            data['ResidentialAreaID'] = ResidentialAreaID
            data['city_name'] = city_name
            data['update_time'] = datetime.datetime.now()
            print(data)
            coll_test.update({'city_name': city_name, 'ResidentialAreaID': ResidentialAreaID}, {'$set': data}, True)
            # 挑出
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print('页面错误')
            channel.basic_publish(exchange='',
                                  routing_key='fgg_comm_id',
                                  body=body,
                                  )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self, name):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.start_community_info, queue='fgg_comm_id',
                              consumer_tag=name)
        channel.start_consuming()


if __name__ == '__main__':
    u = Update_comm_price()
    # 放入队列
    # u.put_rabbit()
    user = coll_user.find_one()['user_name']
    print('user', user)
    u.consume_queue(user)
