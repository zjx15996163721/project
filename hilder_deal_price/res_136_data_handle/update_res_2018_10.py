from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import re
"""
这个文件是用来更新澜斯10月份抓取的数据，格式化，城市，区域，名称
"""
m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection_res_second_2018_10 = m['deal_price']['res_second_2018_10']

collection_match = m['friends']['xzj_yd_res_fj']


for i in collection_res_second_2018_10.find(no_cursor_timeout=True):
    source = 'res'
    city = '上海'
    region = i['area']
    friendsName = i['fullhousingname']

    data = collection_match.find_one({'source': source, 'city': city, 'region': region, 'friendsName': friendsName})

    if data:
        print(data['_id'])
        collection_res_second_2018_10.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': data['city'],
                                                                                       'fj_region': data['region'],
                                                                                       'fj_name': data['fjName'],
                                                                                       'update_time': datetime.utcnow().replace(tzinfo=timezone.utc)}})
        print('更新数据 _id={}'.format(data['_id']))
    else:

        friendsAddress = i['housingaddressall']
        address = re.search('\d+(号|弄|支|支弄|单号|双号|甲号|乙号|丙号|丁号)', friendsAddress, re.S | re.M)

        if address:
            data = collection_match.find_one({'source': source, 'city': city, 'region': region, 'friendsAddress': friendsAddress})

            if data:
                print(data['_id'])

                collection_res_second_2018_10.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': data['city'],
                                                                                               'fj_region': data['region'],
                                                                                               'fj_name': data['fjName'],
                                                                                               'update_time': datetime.utcnow().replace(tzinfo=timezone.utc)}})
                print('更新数据 _id={}'.format(data['_id']))

