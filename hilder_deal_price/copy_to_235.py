from pymongo import MongoClient
from BassClass_backup import Base
import pymongo
from pymongo.errors import BulkWriteError
from lib.log import LogHandler
import time
import asyncio
import aiohttp
import gevent
import threading
from multiprocessing import Process
from gevent import monkey
monkey.patch_all()

log = LogHandler(__name__)
m = MongoClient(host='192.168.0.43', port=27017)
collection_43 = m['fangjia']['deal_price']
n = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_235 = n['fangjia']['deal_price']


# def test_time(func):
#     def get_time():
#         start_time = time.time()
#         func()
#         end_time = time.time()
#         last_time = end_time-start_time
#         print(last_time)
#
#     return get_time
#
#
# @ test_time
def run():
    # threading.Thread(target=copy_to_235).start()
    threading.Thread(target=copy_to_235_reverse).start()


def copy_to_235():
    info_list = []
    for data in collection_43.find(no_cursor_timeout=True).sort('_id', pymongo.DESCENDING):
        info_list.append(data)
        if len(info_list) == 100:
            # jobs = [gevent.spawn(get_data, data) for data in info_list]
            # gevent.wait(jobs)
            for i in info_list:
                threading.Thread(target=get_data, args=(i, )).start()
            info_list.clear()
        else:
            continue


def copy_to_235_reverse():
    info_list = []
    for data in collection_43.find(no_cursor_timeout=True).sort('_id', pymongo.ASCENDING):
        info_list.append(data)
        if len(info_list) == 100:
            # jobs = [gevent.spawn(get_data, data) for data in info_list]
            # gevent.wait(jobs)
            for i in info_list:
                threading.Thread(target=get_data, args=(i, )).start()
            info_list.clear()
        else:
            continue


def get_data(data):
    base = Base()
    base._id = data['_id']
    base.city = data['city']
    base.region = data['region']
    base.district_name = data['district_name']
    base.avg_price = data['avg_price']
    base.house_num = data.get('house_num', None)
    base.unit_num = data.get('unit_num', None)
    base.room_num = data.get('room_num', None)
    base.area = data['area']
    base.total_price = int(int(data['avg_price']) * float(data['area']))
    base.direction = data.get('direction', None)
    base.fitment = data.get('fitment', None)
    base.source = data['source']
    base.room = data.get('room', None)
    base.hall = data.get('hall', None)
    base.toilet = data.get('toilet', None)
    base.height = data.get('height', None)
    base.floor = data.get('floor', None)
    base.trade_date = data['trade_date']
    if data.get('c_date') is not None:
        base.create_date = data.get('c_date')
    else:
        base.create_date = data.get('create_date', None)
    base.url = data.get('url', None)
    # base_dict = base.insert_db()
    base.insert_db()
    # insert_235(base_dict)


    # info_dict = base.insert_db()
    # data_dict_list.append(info_dict)
    # if len(data_dict_list) == 500:
    #     try:
    #         collection_235.insert_many(data_dict_list, ordered=False)
    #         data_dict_list.clear()
    #     except BulkWriteError as e:
    #         print(e)


def insert_235(data):
    try:
        collection_235.insert_one(data)
    except BulkWriteError as e:
        log.info(e)


if __name__ == '__main__':
    # Process(target=copy_to_235).start()
    # Process(target=copy_to_235_reverse).start()
    # run()
    copy_to_235()