from lib.mongo import Mongo
import requests
import time
import datetime
from lib.proxy_iterator import Proxies
p = Proxies()
m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
user_collection = m.connect['friends']['xiaozijia_user']


class Login:
    @classmethod
    def get_cookie(cls):
        count = 0
        cookie_count = 0
        for i in user_collection.find({'status': None, 'cookie': None}, no_cursor_timeout=True):
            login_url = 'http://www.xiaozijia.cn/user/Login?ReturnUrl=http%3A%2F%2Fwww.xiaozijia.cn%2F'
            data = {
                'UserAccount': i['username'],
                'AccountType': 0,
                'Password': i['password'],
                'RememberMe': 'false',
                'returnUrl': 'http://www.xiaozijia.cn/',
            }
            headers = {
                'Host': 'www.xiaozijia.cn',
                'Origin': 'http://www.xiaozijia.cn',
                'Referer': 'http://www.xiaozijia.cn/user/login?returnUrl=http://www.xiaozijia.cn/',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
            }
            s = requests.session()
            try:
                response = s.post(url=login_url, data=data, headers=headers, proxies=next(p))
                print(response.status_code)
                if '该帐号被禁用' in response.text:
                    count += 1
                    print('帐号被禁用的有{}个'.format(count))
                    user_collection.update_one({'username': i['username']},
                                               {'$set': {'status': 1}})
                    continue
            except Exception as e:
                print('登录失败 e={}'.format(e))
                continue
            cookie_list = s.cookies.items()
            cookie_ = ''
            for k in cookie_list:
                key = k[0]
                value = k[1]
                string = key + '=' + value + ';'
                cookie_ += string
            print(cookie_)
            user_collection.update_one({'username': i['username']}, {'$set': {'cookie': cookie_, 'date': datetime.datetime.now()}})
            cookie_count += 1
            print('更新cookie值,到第{}个'.format(cookie_count))


if __name__ == '__main__':
    while True:
        Login.get_cookie()
