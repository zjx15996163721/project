from datetime import datetime
from elasticsearch import Elasticsearch

index_name = 'xiaowushen-6.4.3-2018.11.16'
es = Elasticsearch(hosts='192.168.0.193', port=9200)
print(es.indices.get('xiaowushen-6.4.3-2018.11.16'))

query = {'query': {'match_all': {}}}
res = es.search(index=index_name, doc_type=None,body=query)
for hit in res['hits']['hits']:
    print(hit["_source"]['message'])
print("Got %d Hits:" % res['hits']['total'])
print(res)

# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.now(),
# }
# res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
# print(res['result'])
#
# res = es.get(index="test-index", doc_type='tweet', id=1)
# print(res['_source'])
#
# es.indices.refresh(index="test-index")
#
# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# print("Got %d Hits:" % res['hits']['total'])
# for hit in res['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
