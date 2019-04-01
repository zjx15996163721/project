import requests
import re
import urllib.parse
import json
from lib.standardization import standard_city
from lib.mongo import Mongo

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
collection = m.connect['amap']['amap_road_clean']

host = 'http://poi.map.xiaojukeji.com/mapapi/textsearch?'


def analyzer():
    res = requests.get('http://114.80.150.196:8002/latestLog?')
    info_json = res.json()
    for i in info_json:
        url = i['url']
        house_id = i['id']
        if host in url:
            name_url_encode = re.search('query=(.*?)\&', url, re.S | re.M).group(1)
            name = urllib.parse.unquote(name_url_encode)
            r = requests.get('http://114.80.150.196:8002/fetchBody?id={}'.format(house_id))
            try:
                r_info = r.json()['resBody']
                j = json.loads(r_info)
                result, city = standard_city(j['city'])
                if result:
                    collection.update({'city': city, 'name': name},
                                      {'$set': {'didi': j}})
                    print(city, name)
            except Exception as e:
                print('-')


if __name__ == '__main__':
    analyzer()
