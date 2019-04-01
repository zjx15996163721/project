from pymongo import MongoClient

offline_deal_price = MongoClient(host='192.168.0.43', port=27017)
collection_offline = offline_deal_price['fangjia']['deal_price']


def remove_youda():
    source_list = ['新友达', '友达']
    for source in source_list:
        for i in collection_offline.find({'source': source, 'city': '上海'}, no_cursor_timeout=True):
            collection_offline.remove({'_id': i['_id']})
