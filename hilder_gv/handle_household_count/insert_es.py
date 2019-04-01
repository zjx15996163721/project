from pymongo import MongoClient
from elasticsearch import Elasticsearch
es = Elasticsearch('localhost:9200')
es.indices.create(index='city', ignore=400)
# 删除
query = {
    'query': {
        'match_all': {}
    }
}
es.delete_by_query(index='city', body=query)

# 批量插入
# doc = [
#     {"index": {}},
#     {'name': 'jackaaa', 'age': 2000, 'sex': 'female', 'address': u'北京'},
#     {"index": {}},
#     {'name': 'jackbbb', 'age': 3000, 'sex': 'male', 'address': u'上海'},
#     {"index": {}},
#     {'name': 'jackccc', 'age': 4000, 'sex': 'female', 'address': u'广州'},
#     {"index": {}},
#     {'name': 'jackddd', 'age': 1000, 'sex': 'male', 'address': u'深圳'},
#  ]
# print(es.bulk(index='name', doc_type='str', body=doc))

# 查询
# body = {
#     'query': {
#         'match_all': {}
#     }
# }
# res = es.search(index='name', doc_type='str', body=body)
# print(res)



#
# TEST136client = MongoClient('192.168.0.38', 27007)
# collection_seaweed = TEST136client.get_database("fangjia").seaweed
#
#
# def insert_es():
#     count = 0
#     for i in collection_seaweed.find({"visible": 0, "cat": "district"}):
#         count += 1
#         print(count)
#         i.pop('_id')
#         es.index(index='city', doc_type='str', body=i)
#         print('导入一条数据到es{}'.format(i))
#
#
# if __name__ == '__main__':
#     insert_es()
