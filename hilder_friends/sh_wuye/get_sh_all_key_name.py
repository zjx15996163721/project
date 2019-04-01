import pymongo
from lib.mongo import Mongo

m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
key_coll = m.connect['wuye']['key_name']


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


set_ = set([])
comm_coll = connect_mongodb('114.80.150.198', 27017, 'fangjia', 'seaweed')
# key_coll = connect_mongodb('114.80.150.196', 27777, 'wuye', 'key_name')
list_ = comm_coll.find({'city': '上海'})
count = 0
for i in list_:
    name = i['name']
    for i in name:
        print(i)
        data = {
            '_id': i
        }
        try:
            key_coll.insert(data)
        except Exception as e:
            print('key重复')
    count += 1
    print(count)
