from pymongo import MongoClient
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['count_finish_building_date']

TEST136client = MongoClient('192.168.0.38', 27007)
collection_seaweed = TEST136client.get_database("fangjia").seaweed

count = 0
for i in collection_seaweed.find({"visible" : 0, "cat" : "district"},no_cursor_timeout=True):
    count += 1
    print(count)
    if 'finish_building_date' in i:
        if i['finish_building_date'] and '-' in i['finish_building_date']:
            data = {
                'date': i['finish_building_date'].split('-')[0]
            }
            crawler_collection.insert_one(data)
            print('插入一条数据{}'.format(data))
        elif i['finish_building_date'] and '.' in i['finish_building_date']:
            data = {
                'date': i['finish_building_date'].split('.')[0]
            }
            crawler_collection.insert_one(data)
            print('插入一条数据{}'.format(data))
        else:
            data = {
                'date': i['finish_building_date']
            }
            crawler_collection.insert_one(data)
            print('插入一条数据{}'.format(data))














