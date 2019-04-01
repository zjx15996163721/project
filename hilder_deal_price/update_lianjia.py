from pymongo import MongoClient

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection = m['deal_price']['lianjiazaixian']

count = 0
for i in collection.find(no_cursor_timeout=True):
    count += 1
    print(count)
    _id = i['_id']
    i.update(elevator_configuration=i.pop("packing_space"))
    i.pop('_id')
    collection.find_one_and_update({'_id': _id}, {'$set': i})
    print('更新一条数据')

