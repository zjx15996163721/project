import requests
from lib.mongo import Mongo
import itertools
from xiaozijia_core.register import Register
from xiaozijia_core.login import Login
import time

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
user_collection = m.connect['friends']['xiaozijia_user']

proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
    "host": "http-proxy-sg2.dobel.cn",
    "port": "9180",
    "account": 'FANGJIAHTT7',
    "password": "HGhyd7BF",
}
proxies = {"https": proxy,
           "http": proxy}


def check():
    # cookie_iter = itertools.cycle([_['cookie'] for _ in user_collection.find(no_cursor_timeout=True)])
    headers = {
        # 'Cookie': next(cookie_iter),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
    }
    response = requests.get('http://www.xiaozijia.cn/HouseInfo/3306', headers=headers, proxies=proxies, timeout=10)
    try:
        print(response.json())
    except Exception as e:
        if '登录' in response.content.decode():
            print('账号失效')
            r = Register()
            r.start_register()
            result = r.result
            # 删除老账号并
            for i in user_collection.find():
                user_collection.delete_one({'_id': i['_id']})
            for i in range(16):
                l = Login()
                print(l.get_headers(result))


if __name__ == '__main__':
    check()
    time.sleep(60)
