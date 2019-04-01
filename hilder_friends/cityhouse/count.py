import requests
from cityhouse.citylist import items
from lib.proxy_iterator import Proxies
from lib.mongo import Mongo
import yaml

setting = yaml.load(open('config.yaml'))
mongo_host = setting['cityhouse']['mongo']['host']
mongo_port = setting['cityhouse']['mongo']['port']
user_name = setting['cityhouse']['mongo']['user_name']
password = setting['cityhouse']['mongo']['password']
db_name = setting['cityhouse']['mongo']['db']
db_coll = setting['cityhouse']['mongo']['comm_coll']

p = Proxies()
proxy = next(p)
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36'
}

m = Mongo(host=mongo_host, port=mongo_port, user_name=user_name, password=password)
collection = m.connect[db_name]['cityhouse_9_3']


def count():
    for province in items['items']:
        city_list = province['citys']
        for city in city_list:
            city_code = city['cityCode']
            city_name = city['cityName']
            url = 'http://api.cityhouse.cn/csfc/v2/ha/list?percount=10&proptype=11&page=1&apiKey=4LiEDwxaRaAYTA3GBfs70L&ver=2&city=' \
                  + city_code
            real_num = collection.find({'city': city_name}).count()
            # try:
            #     res = requests.get(url, headers=headers, proxies=proxy)
            #     total = res.json()['totalSize']
            #     print(city_name, total, real_num)
            # except:
            #     print('城市={},请求失败'.format(city_name))
            #     continue
            # if total == 0:
            #     print('当前城市={},暂无数据'.format(city_name))
            #     continue
            print(city_name,real_num)