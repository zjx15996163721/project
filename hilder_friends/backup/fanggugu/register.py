import requests
import time
from rk import RClient
from yanzhengma import get_token, get_phone, get_msg
import pymongo
import random

count = 0


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def yonghuming():
    list_ = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v',
             'b', 'n', 'm', 'o', 'p', '1', '2', '3.png', '4', '5', '6', '7', '8', '9']
    user_name = 'f'+random.choice(list_) * 2 + random.choice(list_) * 2 + random.choice(list_) * 2 + random.choice(
        list_) * 2 + random.choice(list_) * 2 + random.choice(list_) * 2
    print('用户名为：', user_name)
    return user_name


def register(phone):
    coll_insert = connect_mongodb('192.168.0.235', 27017, 'fgg', 'user_info')
    s = requests.session()
    rc = RClient('ruokuaimiyao', 'goojia123456', '95632', '6b8205cf61944329a5841c30e5ed0d5d')
    proxies = {
        'http': 'http://192.168.0.93:4234/'
    }
    c = int(time.time() * 1000)
    s.get('http://www.fungugu.com/ShenQingShiYong/fillInformation', proxies=proxies)
    jrbqiantai = s.cookies.get_dict()['jrbqiantai']
    cookie = 'Hm_lpvt_203904e114edfe3e6ab6bc0bc04207cd' + str(c) + ';Hm_lvt_203904e114edfe3e6ab6bc0bc04207cd' + str(
        c) + ';jrbqiantai=' + jrbqiantai
    headers = {
        'Cookie': cookie,
        'Referer': 'http://www.fungugu.com/ShenQingShiYong/fillInformation',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'
    }
    print(headers)
    while True:
        url = 'http://www.fungugu.com/yzmControlller/refreshPicCode?id=pwdCode&' + str(c)
        response = s.get(url=url, proxies=proxies)
        code = rc.rk_create(response.content, 3040)['Result']
        print('code:', code)
        params = {'code': code,
                  'type': 'pwdCode',
                  }
        code_url = 'http://www.fungugu.com/yzmControlller/verificationPicCode'
        result = s.post(url=code_url, params=params, proxies=proxies)
        print(result.content)
        if 'true' in result.text:
            break
    params = {
        'phone': phone,
        'picCode': code
    }
    # 发送手机号短信
    send_url = 'http://www.fungugu.com/yzmControlller/sendCode'
    result = s.post(url=send_url, params=params, proxies=proxies)
    print(result.content.decode())
    print(phone)
    # phone_verification = get_msg(token, phone)
    phone_verification = input('验证码 ：')
    params = {
        'securityCode': phone_verification,
        'phone': phone
    }
    phone_url = 'http://www.fungugu.com/yzmControlller/verificationSMSCode'
    result = s.post(url=phone_url, params=params, proxies=proxies)
    print('aaa:', result.content)
    user_name = yonghuming()
    params = {
        'keyCode': '',
        'keHuShouJi': phone,
        'yongHuMing': user_name,
        'keHuMiMa': '4ac9fa21a775e4239e4c72317cdca870',
        'quanXianChengShi': '上海',
        'jiGouMingCheng': user_name,
    }
    register_url = 'http://www.fungugu.com/ShenQingShiYong/completionUserInfo'
    result = s.post(url=register_url, params=params, proxies=proxies)
    print(result.text)
    if 'true' in result.text:
        data = {
            'user_name': user_name,
        }
        coll_insert.insert_one(data)
        print('插入成功')
    else:
        print('错误')


if __name__ == '__main__':
    pass
