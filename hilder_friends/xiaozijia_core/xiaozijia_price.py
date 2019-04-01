import requests
from pymongo import MongoClient
import re

m = MongoClient(host='114.80.150.196',
                port=27777,
                username='goojia',
                password='goojia7102')
collection = m['friends']['three_city_month']

city_code = {
    '合肥': '3401',
    '上海': '3101',
    '无锡': '3202',
}


class Price:
    def __init__(self):
        self.headers = {'Cookie': 'ASP.NET_SessionId=mv0mhc1vxufrrofw2htblsd2;',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

    def search(self):
        count = 0
        for i in collection.find():
            name = i['district_name']
            city = i['city']
            region = i['region']
            # print(i)
            # print(r.text)
            #
            info = i['info']
            con_ids = re.findall('<ConstructionId>(.*?)</ConstructionId>', info, re.S | re.M)

            for con_id in con_ids:
                if name in con_id:
                    if region in con_id:
                        print(con_id)
                        count = count + 1
                        collection.update_one({'_id': i['_id']}, {'$set': {'con_id': con_id}})
            print(count)

    def get_price(self):
        for i in collection.find():
            if 'con_id' in i:
                con_id = re.search('\^.*?\^(.*?)\^', i['con_id'], re.S|re.M).group(1)
                print(con_id)
                url = 'http://www.xiaozijia.cn/Chart/GetConPRT/{}'.format(con_id)
                r = requests.get(url=url, headers=self.headers)
                print(r.json())
                collection.update_one({'_id': i['_id']}, {'$set': {'price': r.json()}})