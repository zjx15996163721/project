"""
合并抓取数据

"""
from pymongo import MongoClient

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_merge = m['hilder_gv']['gv_merge']

collection_anjuke = m['hilder_gv']['anjuke']
collection_fangdi = m['hilder_gv']['fangdi']
collection_fanggugu = m['hilder_gv']['fanggugu']
collection_fangtianxia = m['hilder_gv']['fangtianxia']
collection_lianjia = m['hilder_gv']['lianjia']
collection_nanjing = m['hilder_gv']['nanjing']
collection_ningbo = m['hilder_gv']['ningbo']
collection_qingdao = m['hilder_gv']['qingdao']
collection_tongcheng = m['hilder_gv']['tongcheng']
collection_xiamen = m['hilder_gv']['xiamen']
collection_xian = m['hilder_gv']['xian']

count = 0
for i in collection_anjuke.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_fangdi.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_fanggugu.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_fangtianxia.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_lianjia.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_nanjing.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_ningbo.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_qingdao.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)


count = 0
for i in collection_tongcheng.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

count = 0
for i in collection_xiamen.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)


count = 0
for i in collection_xian.find(no_cursor_timeout=True):
    count += 1
    print(count)
    print(i['source'])
    collection_merge.insert_one(i)

