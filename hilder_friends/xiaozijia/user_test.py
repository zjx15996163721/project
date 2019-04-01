"""
小资家手机app用fiddler抓包,抓取均价
"""
import requests
from pymongo import MongoClient
from urllib import parse
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
p = p.get_one(proxies_number=1)
log = LogHandler(__name__)
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_user = m['friends']['xiaozijia_user']


class XzjUser:

    def __init__(self, proxies):
        self.Authorization_list = []
        self.proxies = proxies

    def get_authorization(self):
        count = 0
        for user in collection_user.find({'phone_status': 0}, no_cursor_timeout=True):
            count += 1
            print(count)
            start_url = 'http://www.xiaozijia.cn:8002/Token'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Proxy-Connection': 'keep-alive',
                'Accept': '*/*',
                'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, ja-JP;q=0.8, ko-KR;q=0.7, zh-Hant-CN;q=0.6',
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                'Host': 'www.xiaozijia.cn:8002'
            }
            data = {
                'Password': user['password'],
                'grant_type': 'password',
                'username': user['username'],
            }
            try:
                r = requests.post(url=start_url, data=data, headers=headers, proxies=self.proxies)
                print(r.status_code)
                # if r.status_code != 200:
                #     collection_user.find_one_and_update({'username': user['username']}, {'$set': {'phone_status': 1}})
                #     print('账户失效 username={}, password={}'.format(user['username'], user['password']))

                access_token = r.json()['access_token']
                token_type = r.json()['token_type']
                authorization = token_type + ' ' + access_token
                print(authorization)
            except Exception as e:
                log.error(e)
                continue
            construction_url = 'http://www.xiaozijia.cn:8002/api/v1/BaseData/SearchContrution/3101/' + parse.quote('宛平南路420弄')
            headers = {
                'Connection': 'keep-alive',
                'Host': 'www.xiaozijia.cn:8002',
                'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                'Authorization': authorization,
            }
            try:
                r = requests.get(url=construction_url, headers=headers, proxies=self.proxies)
            except Exception as e:
                log.error(e)
                continue
            print(r.text)
            if '权限不足' in r.text:
                collection_user.find_one_and_update({'username': user['username']}, {'$set': {'phone_status': 1}})
                print('账户失效 username={}, password={}'.format(user['username'], user['password']))
            else:
                collection_user.find_one_and_update({'username': user['username']}, {'$set': {'phone_status': 0}})
                print('有效 username={}, password={}'.format(user['username'], user['password']))


if __name__ == '__main__':
    price = XzjUser(p)
    price.get_authorization()



