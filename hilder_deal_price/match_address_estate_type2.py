import gevent
from pymongo import MongoClient
from lib.match_district import match
from bson import ObjectId
import threading
import pymongo
from gevent import monkey
monkey.patch_all()
n = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection_lianjia = n['deal_price']['lianjiazaixian']


def match_address_estate_type2(data):
    _id = data['_id']

    city = data['city']
    region = data['region']
    district_name = data['district_name']

    match_data = match(city=city, region=region, keyword=district_name)

    if match_data and match_data['flag'] == '精确匹配':
        address = match_data['maddress']

        collection_lianjia.find_one_and_update({'_id': _id}, {'$set': {'address': address}})
        print('更新地址 _id={} address={}'.format(_id, address))

        match_id = match_data['_id']

        m = MongoClient(host='192.168.0.136', port=27017)
        collection_seaweed = m['fangjia']['seaweed']

        seaweed_data = collection_seaweed.find_one({'_id': ObjectId(match_id)})
        if seaweed_data and 'estate_type2' in seaweed_data:
            collection_lianjia.find_one_and_update({'_id': _id}, {'$set': {'estate_type2': seaweed_data['estate_type2']}})
            print('更新地址 _id={} estate_type2={}'.format(_id, seaweed_data['estate_type2']))

        m.close()


if __name__ == '__main__':
    data_list = []
    count = 0
    for i in collection_lianjia.find(no_cursor_timeout=True).sort('_id', pymongo.DESCENDING):
        count += 1
        print('到第{}条'.format(count))
        data_list.append(i)
        if len(data_list) == 50:
            tasks = [gevent.spawn(match_address_estate_type2, data) for data in data_list]
            gevent.wait(tasks)
            data_list.clear()
    tasks = [gevent.spawn(match_address_estate_type2, data) for data in data_list]
    gevent.wait(tasks)
    data_list.clear()


