import asyncio
import yaml
from lib.mongo import Mongo

setting = yaml.load(open('../config.yaml'))
client = Mongo(host=setting['mongo']['host'],
               port=setting['mongo']['port'],
               user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
soldcoll = client[setting['mongo']['db']][setting['mongo']['collection_1']]
listcoll = client[setting['mongo']['db']][setting['mongo']['collection_2']]
rentcoll = client[setting['mongo']['db']][setting['mongo']['collection_3']]

sold = client[setting['mongo']['db']]['soldprice_8_16']
li = client[setting['mongo']['db']]['listprice_8_16']
rent = client[setting['mongo']['db']]['rentprice_8_16']


async def sold_duplicate(count):
    for solddata in soldcoll.find({}, no_cursor_timeout=True).skip(count).limit(1000):
        if sold.find_one({'address': solddata['address'], 'zipcode': solddata['zipcode'],'city':solddata['city']}):
            print('------重复数据-------')
        else:
            sold.insert_one(solddata)
            sold.ensure_index([('address',1),('zipcode',1),('city',1)])
            print('插入sold数据{}'.format(solddata))


async def list_duplicate(count):
    for listdata in listcoll.find({}, no_cursor_timeout=True).skip(count).limit(1000):
        if li.find_one({'address': listdata['address'], 'zipcode': listdata['zipcode'],'city':listdata['city']}):
            print('------重复数据-------')
        else:
            li.insert_one(listdata)
            li.ensure_index([('address',1),('zipcode',1),('city',1)])
            print('插入list数据{}'.format(listdata))


async def rent_duplicate(count):
    for rentdata in rentcoll.find({}, no_cursor_timeout=True).skip(count).limit(10000):
        if rentdata['house_type'] == 'apartment':
            if rent.find_one({'address': rentdata['address'], 'zipcode': rentdata['zipcode'],
                              'room_name': rentdata['room_name'],'city':rentdata['city']}):
                print('------重复数据-------')
            else:
                rent.insert_one(rentdata)
                rent.ensure_index([('address',1),('zipcode',1),('room_name',1),('city',1)])
                print('插入rent数据{}'.format(rentdata))
        else:
            if rent.find_one({'address': rentdata['address'], 'zipcode': rentdata['zipcode'],'city':rentdata['city']}):
                print('------重复数据-------')
            else:
                rent.insert_one(rentdata)
                rent.ensure_index([('address',1),('zipcode',1),('room_name',1),('city',1)])
                print('插入rent数据{}'.format(rentdata))


if __name__ == '__main__':
    count = []
    for i in range(175):
        count.append(i * 10000)
    loop = asyncio.get_event_loop()
    tasks = [rent_duplicate(n) for n in count]
    loop.run_until_complete(asyncio.wait(tasks))
