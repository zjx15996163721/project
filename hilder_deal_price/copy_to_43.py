from pymongo import MongoClient

m = MongoClient(host='192.168.0.43', port=27017)
collection_43 = m['fangjia']['deal_price_12_14']

n = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_235 = n['fangjia']['deal_price_distinct1']

data_list = []

count = 0
for i in collection_235.find(no_cursor_timeout=True):
    count += 1
    print('到第{}条'.format(count))
    data_list.append(i)

    if len(data_list) == 500:

        collection_43.insert_many(data_list)
        print('插入500条数据')

        data_list.clear()

if len(data_list) > 0:
    collection_43.insert_many(data_list)
    print('插入不足条数据')

