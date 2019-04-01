from backup.anew_fanggugu.y666yun import GetPhone
import requests
import re
from lib.mongo import Mongo


class Register(object):
    def __init__(self):
        self.s = requests.session()
        self.g = GetPhone('小资家')
        self.phone = self.g.phone
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.code = ''
        self.m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
        self.coll = self.m.connect['friends']['xiaozijia_user']

    def sent_phone(self):
        sent_url = 'http://www.xiaozijia.cn/User/SendRegisterCheckCode'
        data = {
            'Mobile': self.phone,
            'VerificationCodeType': '1'
        }
        response = self.s.post(sent_url, data=data)
        result = response.json()['Result']
        if result:
            print('发送短信成功，phone="{}"'.format(self.phone))
            self.get_code()
        else:
            print('发送短信错误，phone="{}"'.format(self.phone))

    def get_code(self):
        message = self.g.user_single_get_message()
        if not message:
            self.g = GetPhone('小资家')
            self.phone = self.g.phone
            self.sent_phone()
            self.get_code()
        else:
            self.code = re.search('验证码为:(\d+) ,', message).group(1)
            self.register_user()

    def register_user(self):
        register_url = 'http://www.xiaozijia.cn/User/Register'
        data = {
            'Mobile': self.phone,
            'CheckCode': self.code,
            'LoginPwd': 'goojia123456',
            'InvitationCode': '',
            'IsReadAgreement': 'on',
        }
        response = self.s.post(url=register_url, data=data)
        html = response.json()['msg']
        if html == "登录成功":
            print('注册成功')
            item = {
                'username': self.phone,
                'password': 'goojia123456'
            }
            self.coll.insert_one(item)
            self.g.user_release_phone()
        else:
            print('注册失败，html={}'.format(response.json()))

    def start_register(self):
        self.sent_phone()


if __name__ == '__main__':
    for i in range(90):
        r = Register()
        r.start_register()
