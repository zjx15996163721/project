from xiaozijia_core.y666yun import GetPhone
import requests
import re
from lib.mongo import Mongo
import datetime
from lib.proxy_iterator import Proxies
proxies = Proxies()
proxies = proxies.get_one(proxies_number=1)


class Register(object):
    def __init__(self):
        self.password = 'goojia123456'
        self.s = requests.session()
        self.g = GetPhone('小资家')
        self.phone = self.g.phone
        self.headers = {
            'Connection': 'keep-alive',
            'Host': 'www.xiaozijia.cn:8002',
            'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
        }
        self.code = ''
        self.m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
        self.coll = self.m.connect['friends']['xiaozijia_user']
        self.result = ''

    def sent_phone(self):
        # 发送手机验证码
        sent_url = 'http://www.xiaozijia.cn:8002/api/Account/RegisterPhone?phoneNumber={}'.format(self.phone)
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
        else:
            self.code = re.search('验证码为:(\d+) ,', message).group(1)
            self.register_user()

    def register_user(self):
        register_url = 'http://www.xiaozijia.cn:8002/api/Account/Register'
        data = {
            'Code': self.code,
            'ConfirmPassword': self.password,
            'Email': self.phone,
            'Password': self.password,
            'RegisterType': '0',
            'Source': '6'
        }
        response = self.s.post(url=register_url, data=data, headers=self.headers, proxies=proxies)
        if response.status_code == 200:
            print('注册成功')
            item = {
                'username': self.phone,
                'password': self.password,
                'date': datetime.datetime.now(),
                "phone_status": 1
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
