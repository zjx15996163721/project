import requests
import math
from pymongo import MongoClient
import time
import random
from lib.proxy_iterator import Proxies


p = Proxies()
p = p.get_one(proxies_number=6)
proxy = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": "http-dyn.abuyun.com",
    "port": "9020",
    "user": "HPULN86JD485HB3D",
    "pass": "673E8811D7D77884",
}
proxies = {"https": proxy,
           "http": proxy}
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['deal_price']['res_second_2017']
# coll.create_index('newdiskbargainonid', unique=True)


class Youda:

    def __init__(self):
        self.headers = {
            'accept': 'application/json',
            'content-md5': 'M5Wb9oGTF65EYUnyxaW/XQ==',
            'content-type': 'application/json',
            'Origin': 'http://res.hhhuo.net',
            'Referer': 'http://res.hhhuo.net/index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'x-ca-key': '24934144',
            'x-ca-nonce': 'c5e7c479-7f84-4dcf-a123-1881c08ccb75',
            'x-ca-signature': 'jCzGXDAisoeQNR5WgbUAIbK0lAQCmroy687wFU1axrA=',
            'x-ca-signature-headers': 'x-ca-key,x-ca-nonce,x-ca-stage,x-ca-timestamp',
            'x-ca-stage': 'RELEASE',
            'x-ca-timestamp': str(round(time.time())*1000)
        }
        self.start_url = 'http://aliapi.fanglife.net/api/Third/getbargainlist'

    def start_request(self):
        payload = {
            'accountid': 340,
            'address': '',
            'areas': '',
            'housetrait': '',
            'housetypes': '',
            'maxacreage': '',
            'maxdate': "2018-10-31",
            'maxunitprice': "",
            'maxusd': "",
            'minacreage': "",
            'mindate': "2018-10-01",
            'minunitprice': "",
            'minusd': "",
            'mode': "second",
            'modules': "",
            'newdiskid': "",
            'pageindex': 1,
            'pagesize': 30,
            'plates': "",
            'propertyid': "",
            'sortorders': "",
            'ticket': "aed3f859-a7ad-468f-b2c1-eeffc5ed30ab",
            'timestamp': "1542338604",
            'transactiontypes': "",
            'version': "6.0.0",
            'year': 2018
        }
        r = requests.post(url=self.start_url, data=payload, headers=self.headers)
        print(r.status_code)
        print(r.text)


# if __name__ == '__main__':
#     youda = Youda()
#     youda.start_request()

# start_url = 'https://api.growingio.com/v2/9a859ccc614cae89/web/action'
# start_headers = {
#     'Origin': 'http://res.hhhuo.net',
#     'Referer': 'http://res.hhhuo.net/index',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
# }
# data = {
#     'stm': int(round(time.time())*1000)
# }
# s = requests.session()
# r = s.post(url=start_url, data=data, headers=start_headers)
# print(r.content.decode())
#
# next_url = 'http://aliapi.fanglife.net/api/Third/getbargainlist'
# next_headers = {
#     'Access-Control-Request-Headers': 'content-md5,content-type,x-ca-key,x-ca-nonce,x-ca-signature,x-ca-signature-headers,x-ca-stage,x-ca-timestamp',
#     'Access-Control-Request-Method': 'POST',
#     'Origin': 'http://res.hhhuo.net',
#     'Referer': 'http://res.hhhuo.net/index',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
# }
# next_data = {
#     'accountid': 340,
#     'address': '',
#     'areas': '',
#     'housetrait': '',
#     'housetypes': '',
#     'maxacreage': '',
#     'maxdate': "2018-10-31",
#     'maxunitprice': "",
#     'maxusd': "",
#     'minacreage': "",
#     'mindate': "2018-10-01",
#     'minunitprice': "",
#     'minusd': "",
#     'mode': "second",
#     'modules': "",
#     'newdiskid': "",
#     'pageindex': 1,
#     'pagesize': 30,
#     'plates': "",
#     'propertyid': "",
#     'sortorders': "",
#     'ticket': "aed3f859-a7ad-468f-b2c1-eeffc5ed30ab",
#     'timestamp': "1542338604",
#     'transactiontypes': "",
#     'version': "6.0.0",
#     'year': 2018
# }
# next_r = s.options(url=next_url, data=next_data, headers=next_headers)
# print(next_r.content.decode())

final_url = 'http://aliapi.fanglife.net/api/Third/getbargainlist'

final_headers = {
    'accept': 'application/json',
    'content-md5': '6ANsWZvZVlHaaUzVIpIO1Q==',
    'content-type': 'application/json',
    'Origin': 'http://res.hhhuo.net',
    'Referer': 'http://res.hhhuo.net/index',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'x-ca-key': '24934144',
    'x-ca-nonce': '82bf25f1-4f16-4230-a4ae-ff52368ea00c',
    'x-ca-signature': '8paQRAm9d5N+AgecvLWtZDMBRhDnNuIeLqyvtQRVeWY=',
    'x-ca-signature-headers': 'x-ca-key,x-ca-nonce,x-ca-stage,x-ca-timestamp',
    'x-ca-stage': 'RELEASE',
    'x-ca-timestamp': str(round(time.time())*1000)
}
final_data = {
    'accountid': 340,
    'address': '',
    'areas': '',
    'housetrait': '',
    'housetypes': '',
    'maxacreage': '',
    'maxdate': "2018-10-31",
    'maxunitprice': "",
    'maxusd': "",
    'minacreage': "",
    'mindate': "2018-10-01",
    'minunitprice': "",
    'minusd': "",
    'mode': "second",
    'modules': "housetypes",
    'newdiskid': "",
    'pageindex': 1,
    'pagesize': 30,
    'plates': "",
    'propertyid': "",
    'sortorders': "",
    'ticket': "f9c72002-8d13-4d1c-8738-8f1ef3a0dbf2",
    'timestamp': "1542355933",
    'transactiontypes': "",
    'version': "6.0.0",
    'year': 2018
}

r = requests.post(url=final_url, data=final_data, headers=final_headers)
print(r.status_code)
print(r.content.decode())