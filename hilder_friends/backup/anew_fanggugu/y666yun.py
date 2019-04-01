import requests
import re
import time


class GetPhone(object):
    """
        获取手机号，内置登录，项目，手机号，短信，释放等方法
    """

    def __init__(self, item):
        self.url_index = 'http://api.ema666.com'  # 官网
        self.username = 'miyaosk'  # 账号
        self.password = 'goojia123456'  # 密码
        self.Developer = '3Fe0H59ItdjGN5VFaaFXng%3d%3d'  # 开发者参数
        self.token = ''
        self.item_id = ''
        self.phone = ''
        self.item_name = item
        self.message = ''
        self.s = requests.session()
        self.user_login()
        self.user_get_items()
        self.user_get_phone()

    # 用户登录
    def user_login(self):
        try:
            print('☺☺☺ 正在登陆 ☺☺☺')
            login_url = self.url_index + '/Api/userLogin?uName=' + self.username + '&pWord=' + self.password \
                        + '&Developer=' + self.Developer
            response = self.s.get(login_url)
            self.token = response.text
            print('☺☺☺ 登陆成功 ☺☺☺')
        except Exception as e:
            print('☹☹☹　登录失败,重新登录,%s　☹☹☹' % e)
            self.user_login()

    # 获取项目
    def user_get_items(self):
        try:
            print('☺☺☺　正在获取项目　☺☺☺')
            items_url = self.url_index + '/Api/userGetItems?token=' + self.token + '&tp=ut'
            response = self.s.get(items_url)
            items_list = response.text.split('\n')[:-1]
            for item in items_list:
                # if '房估估' == item.split('&')[1]:
                if self.item_name == item.split('&')[1]:
                    self.item_id = item.split('&')[0]
                    print('☺☺☺　获取项目成功　☺☺☺')
        except Exception as e:
            print('☹☹☹　获取项目失败,重新开始获取,%s　☹☹☹' % e)
            self.user_get_items()

    # 获取手机号码
    def user_get_phone(self):
        try:
            print('☺☺☺　正在获取手机号　☺☺☺')
            phone_url = self.url_index + '/Api/userGetPhone?ItemId=' + self.item_id + '&token=' \
                        + self.token + '&PhoneType=0'
            response = self.s.get(phone_url)
            html = response.text
            if 'False' in html:
                print('☹☹☹　获取手机号失败,重新开始获取　☹☹☹')
                self.user_get_phone()
            else:
                self.phone = re.search('(\d+)', html).group(1)
                print('☺☺☺　获取手机号成功(%s)　☺☺☺' % self.phone)
        except Exception as e:
            print('☹☹☹　获取手机号失败,重新开始获取,%s　☹☹☹' % e)
            self.user_get_phone()

    # 获取短信消息
    def user_single_get_message(self):
        try:
            print('☺☺☺　正在获取（%s）手机号的短信内容　☺☺☺' % self.phone)
            for i in range(12):
                message_url = self.url_index + '/Api/userSingleGetMessage?token=' + self.token \
                              + '&itemId=' + self.item_id + '&phone=' + self.phone
                response = self.s.get(message_url)
                html = response.text
                if 'False' in html:
                    print('☹☹☹　（%s）手机号没有收到短信，等待5秒钟...　☹☹☹' % self.phone)
                    time.sleep(5)
                else:
                    print('☺☺☺　短信内容为：%s　☺☺☺' % html)
                    self.message = html
                    return self.message
            print('获取短信失败')
            self.user_release_phone()
            return False
        except Exception as e:
            print('☹☹☹　获取（%s）手机号的短信内容失败,重新开始获取,%s　☹☹☹' % (self.phone, e))
            self.user_get_phone()

    # 释放手机号
    def user_release_phone(self):
        try:
            release_url = self.url_index + '/Api/userReleasePhone?token=' + self.token + '&phoneList=' \
                          + self.phone + '-' + self.item_id + ';'
            response = self.s.get(release_url)
            html = response.text
            if 'False' in html:
                print('☹☹☹ （%s）手机号释放失败，重新获取　☹☹☹' % self.phone)
                self.user_release_phone()
            else:
                print('☺☺☺ （%s）手机号释放成功 ☺☺☺' % self.phone)
        except Exception as e:
            print('☹☹☹（%s）手机号释放失败,重新开始获取,%s　☹☹☹' % (self.phone, e))
            self.user_get_phone()

    # 开始方法
    def start_crawler(self):
        # 登录
        self.user_login()
        # 获取项目
        self.user_get_items()
        # 获得手机号
        self.user_get_phone()
        # 获取验证码
        # self.user_single_get_message()
        # 释放手机号
        self.user_release_phone()


if __name__ == '__main__':
    r = GetPhone('房估估')
    r.start_crawler()
