'''
对数据多于31的进行补充
'''
from pymongo import MongoClient
import requests
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
import json
client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102')

mongo_collection = client['amap']['street_sichuan']
# test_collection = client['amap']['test_sichuan']

log = LogHandler(__name__)


class AddStreet:
    def __init__(self, proxies):
        self.base_url = 'https://www.amap.com/service/poiInfo?'
        self.proxies = proxies

    # 主函数
    def add_streets(self):
        totals = mongo_collection.find()
        for data in totals:
            poi_info = data['poi_info']
            if len(poi_info) == 31:
                log.info('找到一条长度为31的，city_code={}，street_number={}'.format(data['city_code'],data['street_number']))
                self.send_url(data)

    # 发请求
    def send_url(self, data):
        page = 2
        while True:
            city_code = data['city_code']
            street_number = data['street_number']
            region = data['region']
            detail_street = region + street_number
            map_street = street_number
            payload = {
                'query_type': 'TQUERY',
                'pagesize': '30',
                'pagenum': str(page),
                'qii': 'true',
                'cluster_state': '5',
                'need_utd': 'true',
                'utd_sceneid': '1000',
                'div': 'PC1000',
                'addr_poi_merge': 'true',
                'is_classify': 'true',
                'city': city_code,
                'keywords': detail_street,
            }
            try:
                res = requests.get(self.base_url, proxies=self.proxies, params=payload)
                print(res.url)
            except Exception as e:
                log.error('请求失败，payload={}'.format(payload))
                return
            result = self.check(res, data, map_street)
            if not result:
                break
            page = page + 1
            print(page)

    @staticmethod
    def check(res, data, map_street):
        poi_info = data['poi_info']
        print(res)
        text = res.json()
        try:
            total = int(text['data']['total'])
        except:
            return
        if total == 0:
            return False
        else:
            if text['status'] == '1':
                poi_list = text['data']['poi_list']
                for poi in poi_list:
                    address = poi['address']
                    if map_street in address:
                        dict_text = dict(poi)
                        poi_info.append(dict_text)
                    else:
                        break
                # 注意此处是更新
                if len(poi_info) != 31:
                    mongo_collection.update_one(
                        {'city_code': data['city_code'], 'region': data['region'], 'street_number': data['street_number']},
                        {'$set': {'poi_info': poi_info}})
            else:
                print(res.json())
                log.error('请求失败，status不为1，url = {}'.format(res.url))
            return True


if __name__ == '__main__':
    p = Proxies()
    street = AddStreet(proxies=p.get_one(proxies_number=1))
    street.add_streets()
