"""
匹配
"""
from pymongo import MongoClient
import gevent
import time
import threading
from lib.match_district import match
from gevent import monkey
monkey.patch_all()
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_delete_repeat = m['hilder_gv']['gv_merge_final']
collection_merge = m['hilder_gv']['gv_merge']


def start(i):
    city = i['city']
    region = i['region']
    district_name = i['district_name']
    match_data = match(city=city, region=region, keyword=district_name)
    if match_data:
        if '精确匹配' in match_data['flag']:
            collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': match_data['mcity'],
                                                                                      'fj_region': match_data['mregion'],
                                                                                      'fj_name': match_data['mname'],
                                                                                      'fj_id': match_data['_id'],
                                                                                      'fj_flag': 1}})
            print('匹配一条数据')


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_delete_repeat.find({"fj_flag": None}, no_cursor_timeout=True):
        count += 1
        print(count)
        if len(data_list) == 100:
            tasks = [gevent.spawn(start, data) for data in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            data_list.append(i)
    if len(data_list) > 0:
        tasks = [gevent.spawn(start, data) for data in data_list]
        gevent.joinall(tasks)
        data_list.clear()


