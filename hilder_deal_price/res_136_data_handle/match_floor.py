from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
import time
import threading
import requests
import json
import re
import gevent
import pymongo
"""
这个文件更新136数据库res_esfdealprice数据，添加楼层，总楼层
"""

m = MongoClient(host='192.168.0.136', port=27017)
collection_136 = m['business']['res_esfdealprice']


n = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection_house_loudong = n['fangjia']['house_loudong']


def match(i):
    """
    floor 当前楼层
    totalFloor 总楼层
    lng 经度
    lat 纬度
    location 纬度加经度  比如：31.964981,118.716736
    楼层是int  经纬度是double  最后一个是字符串，拼接起来的
    """

    token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
    url = 'http://open.fangjia.com/address/match'

    _id = i['_id']
    print(i['address'])

    payload = {
        'city': '上海',
        'address': i['address'],
        'category': 'property',
        'token': token
    }
    try:
        r = requests.get(url=url, params=payload, timeout=60)
    except Exception as e:
        print(e)
        return
    text = json.loads(r.text, encoding='utf-8')
    if text['msg'] == 'ok':
        data = text['result']
        if 'floor' in data['searchAddress']:
            floor = data['searchAddress']['floor']
            if '-' in floor:
                floor = int(floor.split('-')[0])
            else:
                floor = int(floor)
        else:
            floor = None

        collection_136.find_one_and_update({'_id': _id}, {'$set': {'floor': floor}})
        print('_id={},更新楼层{}'.format(_id, floor))

        house_num = data['searchAddress'].get('buildingNumber', None)

        room_num = data['searchAddress'].get('roomNumber', None)

        unitNumber = data['searchAddress'].get('unitNumber', '--')

        if 'fjName' in i:
            loudong_name = collection_house_loudong.find_one({'city': i['fjCity'], 'region': i['fjRegion'],
                                                              'name': i['fjName'], 'house_num': house_num,
                                                              'house_num_unit': unitNumber, 'room_num': room_num})

            loudong_name_in_seaweed = collection_house_loudong.find_one({'city': i['fjCity'],
                                                                         'region': i['fjRegion'],
                                                                         'name_in_seaweed': i['fjName'],
                                                                         'house_num': house_num,
                                                                         'house_num_unit': unitNumber,
                                                                         'room_num': room_num})

            if loudong_name and 'all_floor' in loudong_name:
                totalFloor = loudong_name['all_floor']
                if totalFloor in [0, -1, None]:
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                    print('_id={},更新总楼层{}'.format(_id, None))
                else:
                    totalFloor = int(totalFloor)
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': totalFloor}})
                    print('_id={},更新总楼层{}'.format(_id, totalFloor))

            elif loudong_name_in_seaweed and 'all_floor' in loudong_name_in_seaweed:
                totalFloor = loudong_name_in_seaweed['all_floor']
                if totalFloor in [0, -1, None]:
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                    print('_id={},更新总楼层{}'.format(_id, None))
                else:
                    totalFloor = int(totalFloor)
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': totalFloor}})
                    print('_id={},更新总楼层{}'.format(_id, totalFloor))

            else:
                collection_136.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                print('_id={},更新总楼层{}'.format(_id, None))


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_136.find(no_cursor_timeout=True):
        count += 1
        print('到第{}条'.format(count))
        data_list.append(i)
        if len(data_list) == 100:
            # for d in data_list:
            #     threading.Thread(target=match, args=(d,)).start()
            # data_list.clear()
            tasks = [gevent.spawn(match, d) for d in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            continue
    tasks = [gevent.spawn(match, d) for d in data_list]
    gevent.joinall(tasks)
    data_list.clear()
    # for d in data_list:
    #     threading.Thread(target=match, args=(d,)).start()
    # data_list.clear()
