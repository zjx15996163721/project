from streets.all_city_list import city_dict
import yaml
import re
from pymongo import MongoClient
import requests
from gevent import monkey
monkey.patch_all()

setting = yaml.load(open('config.yaml'))
client = MongoClient(host=setting['jquerycitys']['mongo']['host'],
                     port=setting['jquerycitys']['mongo']['port'],
                     username=setting['jquerycitys']['mongo']['user_name'],
                     password=setting['jquerycitys']['mongo']['password']
                     )
db = client[setting['jquerycitys']['mongo']['db']]
collection = db[setting['jquerycitys']['mongo']['collection']]
collection.create_index('street_id',unique=True,name='street_id_index')

base_url = 'http://passer-by.com/data_location/town/{}.json'


def handle_city_url():
    for city_code, city_name in city_dict.items():
        print(city_code, city_name)
        # 匹配后四位，如果后四位为0，则代表为省
        pattern2 = re.compile('\d{2}0{4}')
        # 匹配后两位，如果后两位为0，则代表着属于同一市
        pattern3 = re.compile('\d{3}[^0]{1}0{2}')
        # 传过来一个city_code,首先将其后两位换为00
        town = re.sub('\d{2}$', '00', city_code)
        print(town)
        result3 = re.search(pattern3, town)
        # print(result3)
        if result3:
            town_code = result3.group(0)
            try:
                town_name = city_dict[town_code]
                print(town_name)
            except Exception as e:
                town = re.sub('\d{4}$', '0000', city_code)
                town_name = city_dict[town]
                province_name = city_dict[town]
                print(town_name, province_name)
            #替换为省
            province = re.sub('\d{4}$', '0000', city_code)
            result2 = re.search(pattern2, province)
            if result2:
                province_code = result2.group(0)
                province_name = city_dict[province_code]
                print(province_name)
            else:
                province_name = city_dict[province]
                print(province_name)

        url = base_url.format(int(city_code))
        try:
            response = requests.get(url)
            result = response.json()
            print(type(result))
            results = result.items()
            print(results)
            for street_id,value in results:
                print(street_id,value)
                collection.insert({'province': province_name, 'town': town_name, 'area': city_name, 'street': value,'street_id': street_id})

        except Exception as e:
            f = open('fail_url.txt','a')
            f.write(response.url)
            print(response.url)




