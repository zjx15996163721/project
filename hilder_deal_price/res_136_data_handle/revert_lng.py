from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
import time
# import threading
# import requests
# import json
import re
import gevent
# import pymongo
"""
这个文件更新136数据库res_esfdealprice 坐标
"""

m = MongoClient(host='192.168.0.136', port=27017)
collection_136 = m['business']['res_esfdealprice']


def revert(data):
    # 121.49776,31.306486
    if 'location' in data:
        location = data['location']
        lng = location.split(',')[0]
        lat = location.split(',')[1]
        new_location = lat + ',' + lng
        collection_136.find_one_and_update({'_id': data['_id']}, {'$set': {'location': new_location}})
        print('更新坐标 {}'.format(new_location))


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_136.find(no_cursor_timeout=True):
        count += 1
        print('到第{}条'.format(count))
        data_list.append(i)
        if len(data_list) == 100:
            tasks = [gevent.spawn(revert, d) for d in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            continue
    tasks = [gevent.spawn(revert, d) for d in data_list]
    gevent.joinall(tasks)
    data_list.clear()
