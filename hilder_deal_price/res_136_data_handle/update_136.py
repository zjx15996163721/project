from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
from bson import ObjectId
import threading
import gevent
import pymongo

"""
这个文件更新136数据库res_esfdealprice数据，添加格式化城市，区域，名称，经纬度，坐标
"""
m = MongoClient(host='192.168.0.136', port=27017)
collection_136 = m['business']['res_esfdealprice']

collection_seaweed = m['fangjia']['seaweed']


crawler = MongoClient(host='114.80.150.196',
                      port=27777,
                      username='goojia',
                      password='goojia7102')
crawler_collection_1949 = crawler['deal_price']['res_second_1949_2012']
crawler_collection_2012 = crawler['deal_price']['res_second_2012_2017']
crawler_collection_2017 = crawler['deal_price']['res_second_2017']
crawler_collection_2018 = crawler['deal_price']['res_second_2018_10']


def update(res_data):

    resId = res_data['resId']
    _id = res_data['_id']

    data_1949 = crawler_collection_1949.find_one({'_id': ObjectId(resId)})

    data_2012 = crawler_collection_2012.find_one({'_id': ObjectId(resId)})

    data_2017 = crawler_collection_2017.find_one({'_id': ObjectId(resId)})

    data_2018 = crawler_collection_2018.find_one({'_id': ObjectId(resId)})

    if data_1949:
        if 'fj_name' in data_1949:
            collection_136.find_one_and_update({'_id': _id}, {'$set': {'fjName': data_1949['fj_name'],
                                                                       'fjRegion': data_1949['fj_region'],
                                                                       'fjCity': data_1949['fj_city']}})
            print('更新数据 _id={}, fjName={}, fjRegion={}, fjCity={}'.format(_id, data_1949['fj_name'], data_1949['fj_region'], data_1949['fj_city']))

            data = collection_seaweed.find_one({'cat': 'district', 'status': 0,
                                                'city': data_1949['fj_city'],
                                                'region': data_1949['fj_region'],
                                                'name': data_1949['fj_name']})
            if data:
                if 'lng2' in data:
                    lng = float(data['lng2'] / 10 ** 10)
                    lat = float(data['lat2'] / 10 ** 10)
                    location = str(lng) + ',' + str(lat)
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'lng': lng, 'lat': lat, 'location': location}})
                    print('_id={},更新经纬度{}'.format(_id, location))

    elif data_2012:
        if 'fj_name' in data_2012:
            collection_136.find_one_and_update({'_id': _id}, {'$set': {'fjName': data_2012['fj_name'],
                                                                       'fjRegion': data_2012['fj_region'],
                                                                       'fjCity': data_2012['fj_city']}})
            print('更新数据 _id={}, fjName={}, fjRegion={}, fjCity={}'.format(_id, data_2012['fj_name'], data_2012['fj_region'], data_2012['fj_city']))

            data = collection_seaweed.find_one({'cat': 'district', 'status': 0,
                                                'city': data_2012['fj_city'],
                                                'region': data_2012['fj_region'],
                                                'name': data_2012['fj_name']})
            if data:
                if 'lng2' in data:
                    lng = float(data['lng2'] / 10 ** 10)
                    lat = float(data['lat2'] / 10 ** 10)
                    location = str(lng) + ',' + str(lat)
                    collection_136.find_one_and_update({'_id': _id}, {'$set': {'lng': lng, 'lat': lat, 'location': location}})
                    print('_id={},更新经纬度{}'.format(_id, location))

    elif data_2017:
        if 'fj_name' in data_2017:
            collection_136.find_one_and_update({'_id': _id}, {'$set': {'fjName': data_2017['fj_name'],
                                                                       'fjRegion': data_2017['fj_region'],
                                                                       'fjCity': data_2017['fj_city']}})
            print('更新数据 _id={}, fjName={}, fjRegion={}, fjCity={}'.format(_id, data_2017['fj_name'], data_2017['fj_region'], data_2017['fj_city']))

            data = collection_seaweed.find_one({'cat': 'district', 'status': 0,
                                                'city': data_2017['fj_city'],
                                                'region': data_2017['fj_region'],
                                                'name': data_2017['fj_name']})
            if data:
                if 'lng2' in data:
                    lng = float(data['lng2'] / 10 ** 10)
                    lat = float(data['lat2'] / 10 ** 10)
                    location = str(lng) + ',' + str(lat)
                    collection_136.find_one_and_update({'_id': _id},
                                                       {'$set': {'lng': lng, 'lat': lat, 'location': location}})
                    print('_id={},更新经纬度{}'.format(_id, location))

    elif data_2018:
        if 'fj_name' in data_2018:
            collection_136.find_one_and_update({'_id': _id}, {'$set': {'fjName': data_2018['fj_name'],
                                                                       'fjRegion': data_2018['fj_region'],
                                                                       'fjCity': data_2018['fj_city']}})
            print('更新数据 _id={}, fjName={}, fjRegion={}, fjCity={}'.format(_id, data_2018['fj_name'],
                                                                          data_2018['fj_region'], data_2018['fj_city']))
            data = collection_seaweed.find_one({'cat': 'district', 'status': 0,
                                                'city': data_2018['fj_city'],
                                                'region': data_2018['fj_region'],
                                                'name': data_2018['fj_name']})
            if data:
                if 'lng2' in data:
                    lng = float(data['lng2'] / 10 ** 10)
                    lat = float(data['lat2'] / 10 ** 10)
                    location = str(lng) + ',' + str(lat)
                    collection_136.find_one_and_update({'_id': _id},
                                                       {'$set': {'lng': lng, 'lat': lat, 'location': location}})
                    print('_id={},更新经纬度{}'.format(_id, location))


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_136.find(no_cursor_timeout=True):
        count += 1
        print('到第{}条'.format(count))
        data = {
            'resId': i['resId'],
            '_id': i['_id']
        }
        data_list.append(data)
        if len(data_list) == 100:
            # for d in data_list:
            #     # t = threading.Thread(target=update, args=(d,))
            #     # t.start()
            #     # t.join()
            #     threading.Thread(target=update, args=(d,)).start()
            # data_list.clear()

            tasks = [gevent.spawn(update, d) for d in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            continue

    tasks = [gevent.spawn(update, d) for d in data_list]
    gevent.joinall(tasks)
    data_list.clear()
