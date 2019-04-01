from xiaozijia_core.y666yun import GetPhone
import requests
import re
from lib.mongo import Mongo
import datetime
import random

proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
    "host": "http-proxy-sg2.dobel.cn",
    "port": "9180",
    "account": 'FANGJIAHTT1',
    "password": "HGhyd7BF",
}
proxies = {"https": proxy,
           "http": proxy}


class Register(object):
    def __init__(self):
        self.password = 'xzj' + str(random.randint(0, 5)) + '567yhn'
        self.s = requests.session()
        self.g = GetPhone('小资家')
        self.phone = self.g.phone
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
            'Referer': 'http://www.xiaozijia.cn/'
        }
        self.code = ''
        self.m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
        self.coll = self.m.connect['friends']['xiaozijia_user']
        self.result = ''

    def sent_phone(self):
        # 发送手机验证码
        sent_url = 'http://www.xiaozijia.cn/user/RegisterPhone'
        data = {
            'phoneNumber': self.phone,
        }
        try:
            response = self.s.post(sent_url, data=data, headers=self.headers, proxies=proxies)
            print(response.text)
            result = response.json()['Success']
        except Exception as e:
            return

        if result:
            print('发送短信成功，phone="{}"'.format(self.phone))
            self.get_code()
        else:
            print('发送短信错误，phone="{}"'.format(self.phone))

    def get_code(self):
        message = self.g.user_single_get_message()
        if not message:
            print('do nothing')
            pass
            # self.g = GetPhone('小资家')
            # self.phone = self.g.phone
            # # self.sent_phone()
            # self.get_code()
        else:
            self.code = re.search('验证码为:(\d+) ,', message).group(1)
            self.register_user()

    def register_user(self):
        register_url = 'http://www.xiaozijia.cn/user/RegisterAccount'
        data = {
            'UserAccount': self.phone,
            'CheckCode': self.code,
            'loginpwd': self.password,
            'InvitationCode': None,
            'isreadagreement': 'on'
        }
        response = self.s.post(url=register_url, data=data, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36', 'Host': 'www.xiaozijia.cn', 'Origin': 'http://www.xiaozijia.cn', 'Referer': 'http://www.xiaozijia.cn/user/register?ReturnUrl=', 'Upgrade-Insecure-Requests': '1'}, proxies=proxies)
        if response.status_code == 200:
            print('注册成功')
            item = {
                'username': self.phone,
                'password': self.password,
                'date': datetime.datetime.now()
            }
            self.result = item
            self.coll.insert_one(item)
            self.g.user_release_phone()
        else:
            print('注册失败，html={}'.format(response.text))


if __name__ == '__main__':
    while True:
        r = Register()
        r.sent_phone()
