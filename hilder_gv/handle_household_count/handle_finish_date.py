from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
import gevent
TEST136client = MongoClient('192.168.0.38', 27007)
collection_seaweed = TEST136client.get_database("fangjia").seaweed


def start(i):
    if 'household_count' in i:
        if i['household_count'] in [0, 0.0]:
            print(i)
            # collection_seaweed.update_one({'_id': i['_id']}, {'$set': {'household_count': None}})
            # update_count += 1
            # print('更新了{}条'.format(update_count))
            # print('更新一条数据')


if __name__ == '__main__':

    count = 0
    data_list = []
    for i in collection_seaweed.find({"visible": 0, "cat": "district"}):
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
