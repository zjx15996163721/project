import datetime
from pymongo import MongoClient


m = MongoClient(host='192.168.0.43', port=27017)
collection = m['fangjia']['deal_price']

m2 = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')

new_collection = m2['deal_price']['from_43']


def count():
    count = 0
    for i in collection.find({'create_date': {'$gt': datetime.datetime(2018, 12, 1, 8, 10, 37, 22000)}}):
        # i.pop('_id')
        print(i['source'])
        # if '澜斯' not in i['source'] or '友达' not in i['source']:
        count += 1
        print(count)
            # new_collection.insert_one(i)
            # print('插入一条数据{}'.format(i))


if __name__ == '__main__':
    count()
