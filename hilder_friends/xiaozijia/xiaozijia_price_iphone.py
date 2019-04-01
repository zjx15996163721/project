"""
小资家手机app用fiddler抓包,抓取均价
"""
import requests
from pymongo import MongoClient
from lib.proxy_iterator import Proxies
p = Proxies()

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')


collection = m['friends']['xiaozijia_comm']
collection_user = m['friends']['xiaozijia_user']

Authorization_list = []
for user in collection_user.find(no_cursor_timeout=True):
    start_url = 'http://www.xiaozijia.cn:8001/Token'
    headers = {
        'User-Agent': 'xiao zi jiaiOS/1.1.1 (iPhone; iOS 11.4.1; Scale/2.00)',
        'Host': 'www.xiaozijia.cn:8001'
    }
    # 'Password=xzj1567yhn&grant_type=password&username=15143555243'
    data = {
        'Password': user['password'],
        'grant_type': 'password',
        'username': user['username']
    }
    try:
        r = requests.post(start_url, data=data, headers=headers, proxies=next(p))
        print(r.text)
        access_token = r.json()['access_token']
        token_type = r.json()['token_type']
        Authorization = token_type + ' ' + access_token
        print(Authorization)
        Authorization_list.append(Authorization)
        Authorization_list.append(Authorization)
        Authorization_list.append(Authorization)
    except Exception as e:
        print(e)
Authorization_list.reverse()
print(Authorization_list)
Authorization_iter = iter(Authorization_list)


def get_price():
    for i in collection.find({"CityGBCode": "3101"}, no_cursor_timeout=True):
        # if 'comm_unknow_id' in i.keys() and 'Address' in i.keys():
        if 'ResultMessage' in i.keys() and 'comm_unknow_id' in i.keys() and 'Address' in i.keys():
            if i['ResultMessage'] == '模型估价' or i['ResultMessage'] == '自动估价' or i['ResultMessage'] == '请输入缺少的参数' or i['ResultMessage'] == '案例较少' or i['ResultMessage'] == '案例不足' or i['ResultMessage'] is None:
                if 'unit_price' not in i or i['unit_price'] == 0 or i['unit_price'] == 0.0:
                    # todo 请求均价
                    headers = {
                        'User-Agent': 'xiao zi jiaiOS/1.1.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                        'Host': 'www.xiaozijia.cn:8001',
                        'Authorization': next(Authorization_iter)
                    }
                    data = {
                        'CId': i['comm_unknow_id'],
                        "CityId": "310100",
                        "BulidArea": "100",
                        'Address': i['Address'],
                        # "IsQueryPay": True,
                        # "IsAdjustPay": True,
                        # "IsRGXJPay": True
                    }
                    # '{"CId":"18018","HId":"9852046","HName":"103","UName":"8号","FullName":"上南三村8号103","BulidArea":"100","IsQueryPay":false,"Address":"浦东新区上南三村","CityId":"310100","UId":"421869","IsAdjustPay":false,"CName":"上南三村","AreaId":"310115007","IsRGXJPay":false}'
                    try:
                        url = 'http://www.xiaozijia.cn:8001/api/v1/Order/order/House'
                        response = requests.post(url, data=data, headers=headers, proxies=next(p))
                        print(response.text)
                        print(response.status_code)
                        if response.status_code == 200:
                            try:
                                if 'ResultMessage' in response.json():
                                    collection.update_one({'ConstructionId': i['ConstructionId']},
                                                          {'$set': {'ResultMessage': response.json()['ResultMessage'],
                                                                    'info': response.text,
                                                                    'unit_price': int(response.json()['UnitPrice'])}})
                                    print('更新均价{}和ResultMessage{}'.format(int(response.json()['UnitPrice']),
                                                                          response.json()['ResultMessage']))
                            except Exception as e:
                                print('无法序列化 e={}'.format(e))
                        else:
                            print('error')
                    except Exception as e:
                        print(e)


if __name__ == '__main__':

    get_price()
