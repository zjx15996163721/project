import requests
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit

r = Rabbit('127.0.0.1', 5673)
channel = r.get_channel()

m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
coll = m.connect['fgg']['comm']


class Fgg:

    def __init__(self):
        self.headers = {
            'Authorization': "",
        }

        self.ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-pro.abuyun.com", "port": "9010",
                                                                  "user": "HRH476Q4A852N90P",
                                                                  "pass": "05BED1D0AF7F0715"}
        self.proxies = {
            'http': self.ip,
            'https': self.ip,
        }
        self.s = requests.session()

    def login(self):
        url_login = "http://fggfinance.yunfangdata.com/WeChat/webservice/doLogin"
        querystring = {"openid": "ohWOiuP_gteNNJemGpvDG1axnbBc", "password": "4ac9fa21a775e4239e4c72317cdca870",
                       "userName": "asdfasdfasdf"}
        payload = "openid=ohWOiuP_gteNNJemGpvDG1axnbBc&password=4ac9fa21a775e4239e4c72317cdca870&userName=asdfasdfasdf"
        headers_login = {
            'Content-Length': "0",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
            'Cache-Control': "no-cache",
        }
        response = self.s.post(url_login, data=payload, headers=headers_login, params=querystring)
        access_token = response.json()['data']['access_token']['access_token']
        token_type = response.json()['data']['access_token']['token_type']
        authorization = token_type + ' ' + access_token
        print(authorization)
        self.headers['Authorization'] = authorization

    def start_crawler(self, ch, method, properties, body):
        try:
            print(body.decode('utf-8'))
            url = "http://fggfinance.yunfangdata.com/WeChat/JinRongGuZhi/getFangWuZuoLuo?cityNamePy=" + "shanghai" \
                  + "&id=" + body.decode('utf-8') + "&type=xiaoqu"
            response = self.s.get(url, headers=self.headers)
            print(response.json())
            if response.json()['success']:
                if response.json()['data']:
                    data = response.json()
                    data['comm_id'] = body.decode('utf-8')
                    data['city'] = '上海'
                    # coll.insert_one(data)
            else:
                self.login()
                channel.queue_declare(queue='fgg_number')
                channel.basic_publish(exchange='',
                                      routing_key='fgg_number',
                                      body=body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            channel.queue_declare(queue='fgg_number')
            channel.basic_publish(exchange='',
                                  routing_key='fgg_number',
                                  body=body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(consumer_callback=self.start_crawler, queue='fgg_number')
        channel.start_consuming()


if __name__ == '__main__':
    fgg = Fgg()
    fgg.login()
    fgg.consume_queue()
