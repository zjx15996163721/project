import gevent
from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
from district_match.match_seaweed import match
from bson import ObjectId

client = MongoClient('mongodb://goojia:goojia7102@192.168.0.235:27777', connect=False)
district_complete = client['fangjia']['district_complete']

def to_match(i):
    match_info = match(i['city'], **{'region': i['region'], 'name': i['district_name'], 'category': 'property'})
    if match_info:
        if '精确匹配' in match_info['flag']:
            district_complete.update_one({'_id': i['_id']},
                                         {'$set': {'fj_id': match_info['_id'], 'fjName': match_info['mname']}})
            print('精确匹配')

if __name__ == '__main__':

    new = []
    n = 0
    m = 0
    for i in district_complete.find({'source':'fangtianxia'}):
        n += 1
        print(n)
        new.append(i)
        if len(new) == 50:
            tasks = [gevent.spawn(to_match, data) for data in new]
            gevent.joinall(tasks)
            new.clear()
    if len(new) > 0:
        tasks = [gevent.spawn(to_match, data) for data in new]
        gevent.joinall(tasks)

