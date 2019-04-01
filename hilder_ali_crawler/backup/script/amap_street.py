from gevent import monkey

monkey.patch_all()
from lib.mongo import Mongo
import requests
import gevent

client = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102').connect
coll = client['amap']['amap_street']
coll_1 = client['amap']['street_info']
proxy_url = 'http://dev.kuaidaili.com/api/getproxy/?orderid=982168408884810&num=500&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=1&format=json&sep=1    '
coll_1.create_index('name',unique=True)

def fetch():
    payloads = [{
        'query_type': 'TQUERY',
        'pagesize': '20',
        'pagenum': '1',
        'qii': 'true',
        'cluster_state': '5',
        'need_utd': 'true',
        'utd_sceneid': '1000',
        'div': 'PC1000',
        'addr_poi_merge': 'true',
        'is_classify': 'true',
        'city': '310000',
        'keywords': data['street'],
    } for data in coll.find({'status': 0}).limit(500)]

    res = requests.get(proxy_url)
    proxy_list = res.json()["data"]["proxy_list"]
    tasks = [gevent.spawn(amap_request,payload,proxy) for payload,proxy in zip(payloads,proxy_list)]
    gevent.joinall(tasks)


def amap_request(payload,proxy):
    url = 'http://www.amap.com/service/poiInfo?'
    proxies = {'http':'http://'+proxy}
    try:
        res = requests.get(url, proxies=proxies, params=payload)
        print(res.text)
        if payload['keywords'] in res.json()['data']['poi_list'][0]['address']:
            coll.update({'street':payload['keywords']},{'$set':{'status':1}})
            try:
                coll_1.insert_one(res.json()['data']['poi_list'][0])
                print('已插入数据{}'.format(res.json()))
            except:
                print('重复数据')

    except Exception as e:
        print('{},error={}'.format(url,e))

if __name__ == '__main__':
    while True:
        fetch()