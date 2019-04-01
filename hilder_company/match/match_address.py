"""
地址匹配
"""

from pymongo import MongoClient
import redis
import requests
import json
import re
r = redis.Redis(host='localhost', port='6379')
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
company_crawler_merge = m['company']['company_merge']


def match():
    count = 0
    for i in company_crawler_merge.find(no_cursor_timeout=True):
        count += 1
        print(count)
        try:
            token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
            url = 'http://open.fangjia.com/address/match'
            for num in range(len(i['address'])):
                address = i['address'][num]
                payload = {
                    'city': i['fj_city'],
                    'address': address,
                    'category': 'office',
                    'token': token
                }
                try:
                    r = requests.get(url=url, params=payload)
                    data = r.json()['result']
                    # # 可信度
                    # credit = data['credit']
                    # # 省份
                    # province = data['province']
                    # # 城市
                    # city = data['city']
                    # # 区域
                    # district = data['district']
                    # # 板块
                    # block = data['block']
                    # # lng 经度
                    # lng = data['lng']
                    # # lat 纬度
                    # lat = data['lat']

                    if 'address' in data.keys() and 'id' in data.keys() and 'name' in data.keys():
                        # 地址
                        match_address = data['address']
                        # id
                        office_building_id = data['id']
                        # 写字楼名称
                        match_name = data['name']
                        try:
                            room = re.search('\d{3,6}(室|房|号房|户|铺)$', address, re.S | re.M).group()
                        except:
                            room = None
                        company_crawler_merge.find_one_and_update({'company_name': i['company_name'], 'fj_city': i['fj_city']}, {'$set': {'id': office_building_id, 'match_name': match_name, 'match_address': match_address, 'match_room': room}})
                        print('更新一条数据')
                        break
                    else:
                        print('匹配不到')
                        continue
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    match()


