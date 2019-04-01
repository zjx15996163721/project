from pymongo import MongoClient
import pymongo
"""
这个文件是用来更新43 澜斯成交数据，更新格式化城市，区域，名称
"""
m = MongoClient(host='192.168.0.43', port=27017)
collection_43 = m['fangjia']['deal_price']

n = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection_res_second_2018_10 = n['deal_price']['res_second_2018_10']

for i in collection_res_second_2018_10.find({"fj_flag": 1}, no_cursor_timeout=True):
    city = i['fj_city']
    region = i['fj_region']
    district_name = i['fj_name']
    source = '澜斯'
    try:
        data = collection_43.find({'city': city, 'district_name': district_name, 'source': source}, no_cursor_timeout=True).sort('_id', pymongo.DESCENDING)[0]

        collection_43.find_one_and_update({'_id': data['_id']}, {'$set': {'city': city, 'region': region, 'district_name': district_name}})
        print('更新一条数据 ')
    except Exception as e:
        print(e)


