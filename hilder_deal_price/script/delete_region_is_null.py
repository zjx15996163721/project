"""
删除区域为空的
fangjia/comseaweeds
"""
from pymongo import MongoClient
from lib.standardization import standard_city

online_deal_price = MongoClient(host='192.168.0.43', port=27017)
# online_deal_price = MongoClient(host='114.80.150.198', port=27017)
collection = online_deal_price['fangjia']['deal_price']

offline_deal_price = MongoClient(host='114.80.150.198', port=27017)
collection_offline = offline_deal_price['fangjia']['comseaweeds']


def delete_region():
    count = 0
    for i in collection.find({'region': None}, no_cursor_timeout=True):
        city = i['city']
        name = i['district_name']
        result, city_fj = standard_city(city)
        if result:
            d = collection_offline.find_one({'city': city_fj, 'name': name})
            if d:
                print('库里小区名={}, 成交小区名={}'.format(d['name'], name))
                collection.update_one({'_id': i['_id']}, {'$set': {'region': d['region']}})
            a = collection_offline.find_one({'city': city_fj, 'alias': name})
            if a:
                print('找到成交别名了,库里小区名={}, 成交小区名={}'.format(a['name'], name))
                collection.update_one({'_id': i['_id']}, {'$set': {'region': a['region']}})
        else:
            print('匹配不到')
            collection.remove({'_id': i['_id']})
            count = count + 1
            continue
    print('delete count={}'.format(count))
