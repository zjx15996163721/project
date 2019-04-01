import requests
from backup.anew_fanggugu.y666yun import GetPhone
from backup.anew_fanggugu.rk import RClient
import re


class Register(object):
    def __init__(self):
        self.g = GetPhone('房估估')
        self.phone = self.g.phone
        self.s = requests.session()
        self.r = RClient('ruokuaimiyao', 'goojia123456', '95632', '6b8205cf61944329a5841c30e5ed0d5d')
        self.code = ''
        self.phone_code = ''

    def verify_phone(self):
        verify_url = 'http://fggfinance.yunfangdata.com/WeChat/shenQingShiYong/checkPhoneExist?phone=' + self.phone
        response = self.s.get(verify_url)
        html = response.json()
        if html['success']:
            print('此手机号已经注册过，请换个手机号。')
            self.g.user_release_phone()
        else:
            self.get_image()
            self.sent_picture_code()

    def get_image(self):
        image_url = 'http://fggfinance.yunfangdata.com/WeChat/shenQingShiYong/refreshPicCode'
        response = self.s.get(image_url)
        with open('sad.jpg', 'wb') as f:
            f.write(response.content)
        code = self.r.rk_create(response.content, 3040)['Result']
        print(code)
        self.code = code

    def sent_picture_code(self):
        picture_code_url = 'http://fggfinance.yunfangdata.com/WeChat/shenQingShiYong/sendPhoneVerificationCode?phone=' \
                           + self.phone + '&picCode=' + self.code
        response = self.s.get(picture_code_url)
        html = response.json()
        if html['success']:
            print('发送短信成功，请注意查收')
            self.get_message()
            self.g.user_release_phone()
        else:
            print(html)
            self.get_image()
            self.sent_picture_code()

    def get_message(self):
        message = self.g.user_single_get_message()
        phone_code = re.search('验证码为(\d+)，', message, re.S | re.M).group(1)
        self.phone_code = phone_code


if __name__ == '__main__':
    r = Register()
    r.verify_phone()
