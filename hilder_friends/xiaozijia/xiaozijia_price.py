import requests
import re
from pymongo import MongoClient
from lib.proxy_iterator import Proxies
import pika
import itertools
import json
import time
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673))
# channel = connection.channel()
# channel.queue_declare(queue='xzj_cid')

p = Proxies()

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')

collection = m['friends']['xiaozijia_comm']
collection_user = m['friends']['xiaozijia_user']
collection_building = m['friends']['xiaozijia_build']
collection_house = m['friends']['xiaozijia_house']
collection_detail = m['friends']['xiaozijia_detail']

cookie_list = []
for i in collection_user.find():
    if 'cookie' in i.keys():
        cookie_list.append(i['cookie'])
        cookie_list.append(i['cookie'])
        cookie_list.append(i['cookie'])


cookie_iter = iter(cookie_list)

# headers = {
#     'Cookie': 'UM_distinctid=165ae11b898145c-0cb39ea0102be4-1033685c-1aeaa0-165ae11b89955; CNZZDATA1261485443=1278352362-1536223721-%252F%252Fwww.xiaozijia.cn%252F%7C1536230174; ASP.NET_SessionId=ljclydfzzajvvc4zalmvppcz; 18584=webim-visitor-QF3BQC7G98XX4G3MX4K8; Hm_lvt_a9c54182b3ffd707e45190a9a35a305f=1540787980; city_Info={"PinYin":"ShangHai","PID":31,"PYHC":"S ","CityCode":"310100","CityId":3101,"CityName":"ä¸æµ·å¸","CityPY":"SH","IsEvaluation":true,"IsModel":false,"IsTax":false,"ServiceName":"","ServiceTel":"","OCityId":0,"Hot":1,"Sort":998}; u_Info=%7B%22UserId%22%3A%22f514221d-90c3-4d07-afac-febc489dbe3c%22%2C%22ImgUrl%22%3A%22%22%2C%22NikeName%22%3A%2218402867698%22%2C%22BeanBalance%22%3A0%2C%22GiftBeanBalance%22%3A0%7D; .AspNet.ApplicationCookie=QezYBW3iMbPXBM4gt9rQWqJvsNS41pjIuqVjq_KlgSZHJuJwXODADmYr7FvBFMwIL7BF5WT8pSxUuzBLXUAbAQhHKyaXShjIigek_6kAH8KCUeon_9bAaee5_5XYNoufJRlvvEbaMSDUac1NM3IxhhLXWRWfPXk-UqVddb8qelBPprjC5noIy9yOUI31nNe5Hwaet3frMxAVnrFiYio6wjwuwYBZ5ASKqORV0ltt5ehAnP1dPaBPFg-uZxCd6p_AFRjCsMOyJkr-RvEL0ahT6ogSfDc3tBoGdQ60TcAQjQhUhseuAe6uQsAaHH_ZHfe-3BKoaQBmIkmmuD4938PH4c36Yk5DU5I1-LtxsLUi3-PZ2GCD2sNU5NxOWTkLQgzCGeuuPL1Go-d6DF3wJHemV9dbuSBJk7lWo-kXGa-MNyE3Xdt3n3upBfHVFMPl7LIarvoF6KtstWszwK6_OoTh_KMhpwFCqAZpIyVZHrHiZePI5c47H0t7GprJuFesVHaO; Hm_lpvt_a9c54182b3ffd707e45190a9a35a305f=1541067899',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
# }
#
#
# def get_comm_by_comm_name(CityGBCode, ConstructionAlias, ConstructionPhaseId, ConstructionId):
#     url = 'http://www.xiaozijia.cn/SearchCUH/{}/{}'.format(CityGBCode,
#                                                            ConstructionAlias)
#
#     try:
#         r = requests.get(url=url, headers=headers, proxies=next(p))
#         comm_unknow_id = re.search(
#             '<ConstructionId>.*\^.*\^{}\^(.*?)\^.*\^.*\|</ConstructionId>'.format(ConstructionPhaseId), r.text,
#             re.S | re.M).group(1)
#
#         print(comm_unknow_id)
#         collection.update_one({'ConstructionId': ConstructionId}, {'$set': {'comm_unknow_id': comm_unknow_id}})
#         channel.basic_publish(exchange='',
#                               routing_key='xzj_cid',
#                               body=json.dumps({
#                                   'cid': comm_unknow_id,
#                                   'citycode': CityGBCode
#                               }))
#     except Exception as e:
#         print(e)


def evaluate():
    for i in collection.find({"CityGBCode": "3101"}, no_cursor_timeout=True):
        if 'ResultMessage' not in i.keys():
            get_price(i)
        elif 'ResultMessage' in i.keys():
            if '不可估' not in i['ResultMessage']:
                if 'unit_price' not in i:
                    get_price(i)


def get_price(info):
    try:
        price_url = 'http://www.xiaozijia.cn/order/GetQueryPrice'
        # 10个参数
        ConstructionId = info['ConstructionId']
        building_data = collection_building.find_one({'ConstructionId': ConstructionId})
        BId = building_data['Id']
        UName = building_data['Name']
        house_data = collection_house.find_one({'ConstructionId': ConstructionId})
        HId = house_data['Id']
        HName = house_data['Name']
        print('开始请求')
        payload = {"CId": int(info['comm_unknow_id']), "CPId": info['ConstructionPhaseId'], "BuildArea": "88", "City": 310100,
                   "Address": info['Address'], "FullName": info['ConstructionName'] + UName + HName, "BId": str(BId), "HId": str(HId),
                   "HName": HName, "UName": UName}
        print(payload)
        request_cookie = next(cookie_iter)
        try:
            r = requests.post(url=price_url, data=payload,
                              headers={
                                  'Host': 'www.xiaozijia.cn',
                                  'Origin': 'http://www.xiaozijia.cn',
                                  'X-Requested-With': 'XMLHttpRequest',
                                  'Referer': 'http://www.xiaozijia.cn/Evaluation/Evaluation',
                                  "cookie": request_cookie,
                                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'},
                              proxies=next(p))
            print(r.text)
            print(r.status_code)
            if r.status_code == 200:
                try:
                    if 'ResultMessage' in r.json():
                        collection.update_one({'ConstructionId': info['ConstructionId']},
                                              {'$set': {'ResultMessage': r.json()['ResultMessage'],
                                                        'info': r.text,
                                                        'unit_price': int(r.json()['UnitPrice'])}})
                        print('更新均价{}和ResultMessage{}'.format(int(r.json()['UnitPrice']), r.json()['ResultMessage']))
                        if int(r.json()['UnitPrice']) == 0:
                            cookie_list.append(request_cookie)
                except Exception as e:
                    print('无法序列化 e={}'.format(e))
            elif r.status_code == 429:
                print('cookie失效')
        except Exception as e:
            print(e)
    except Exception as e:
        print('key错误')


# def analyzer_price():
#     count = 0
#     for comm in collection.find({"CityGBCode": "3101"}, no_cursor_timeout=True):
#         if 'info' in comm:
#             count += 1
#             print(count)
#             comm_info_json = json.loads(comm['info'])
#             unit_price = comm_info_json['UnitPrice']
#             collection.update_one({'_id':comm["_id"]},
#                                   {'$set': {'unit_price': int(unit_price)}})
#         else:
#             continue


if __name__ == '__main__':
    # for i in collection.find({"CityGBCode": "3101"},no_cursor_timeout=True):
    #     if 'comm_unknow_id' in i:
    #         print('已经存在')
    #     else:
    #         ConstructionAlias Address ConstructionAlias
    # get_comm_by_comm_name(i['CityGBCode'], i['ConstructionAlias'], i['ConstructionPhaseId'], i['ConstructionId'])

    evaluate()
