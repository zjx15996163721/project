from pymongo import MongoClient
import time
import re
from datetime import datetime
from lib.match_district import match
from collections import Counter
""" 这个文件是用来取两个字符串之间 相同的字符串"""
m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection_res_2018 = m['deal_price']['res_second_2018_11']


for i in collection_res_2018.find({"fj_name": None}):
    fullhousingname = i['fullhousingname']
    print(fullhousingname)
    newdiskname = i['newdiskname']
    print(newdiskname)
    Counter(fullhousingname)
    Counter(newdiskname)
    c = Counter(fullhousingname) & Counter(newdiskname)
    new_name = "".join(c.keys())
    print(new_name)
    data = match(city='上海', region=i['area'], keyword=new_name)
    print(data)
    if data:
        if data['flag'] == '精确匹配':
            collection_res_2018.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': data['mcity'],
                                                                                 'fj_region': data['mregion'],
                                                                                 'fj_name': data['mname'],
                                                                                 'fj_flag': 1,
                                                                                 'update_time': datetime.utcnow()}})
            print('更新一条数据 fj_name={}'.format(data['mname']))

# count = 0
# for i in collection_res_2018.find({'fj_flag': 1}):
#     if '地下' in i['houseaddress']:
#         collection_res_2018.find_one_and_update({'_id': i['_id']}, {'$set': {'floor': None}})














