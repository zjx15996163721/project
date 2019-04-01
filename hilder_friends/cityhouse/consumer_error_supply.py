import re
import requests
from lxml import etree
import yaml
from cityhouse.citylist import items
from lib.proxy_iterator import Proxies
from lib.mongo import Mongo
from lib.log import LogHandler
import datetime

log = LogHandler(__name__)
setting = yaml.load(open('config.yaml'))
p = Proxies()
mongo_host = setting['cityhouse']['mongo']['host']
mongo_port = setting['cityhouse']['mongo']['port']
user_name = setting['cityhouse']['mongo']['user_name']
password = setting['cityhouse']['mongo']['password']
db_name = setting['cityhouse']['mongo']['db']
db_coll = setting['cityhouse']['mongo']['comm_coll']

m = Mongo(host=mongo_host, port=mongo_port, user_name=user_name, password=password)
collection = m.connect[db_name][db_coll]

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36'
}
proxy = next(p)


def comm_supply():
    with open('./log/cityhouse.consumer.log', 'r') as f:
        lines = f.readlines()
        lines.reverse()
        for line in lines:
            if re.search('ERROR (http://.*?)请求失败', line):
                url = re.search('ERROR (http://.*?)请求失败', line).group(1)
                code = re.search('ERROR http://(.*?).cityhouse', line).group(1)
                for province in items['items']:
                    city_list = province['citys']
                    for city in city_list:
                        city_code = city['cityCode']
                        city_name = city['cityName']
                        if code == city_code:
                            cityname = city_name
                            fetch(cityname, url)


def fetch(city_name, url):
    co_id = re.search('id=(.*?)&',url).group(1)
    res = requests.get(url, headers=headers, proxies=proxy)
    if res.status_code == 200:
        data = res.content
        cityname = city_name
        name = parse(data, '//name/text()')
        district = parse(data, '//district/text()')
        street = parse(data, '//street/text()')
        comm_type = parse(data, '//incomehouse/text()')
        kpdate = parse(data, '//kpdate/text()')
        location = parse(data, '//location/text()')
        build_size = parse(data, '//item[@name="建筑面积"]/text()')
        land_size = parse(data, '//item[@name="占地面积"]/text()')
        green_rate = parse(data, '//item[@name="绿化率"]/text()')
        volumetric_rate = parse(data, '//item[@name="容积率"]/text()')
        fee = parse(data, '//item[@name="物业费"]/text()')
        certificate = parse(data, '//item[@name="证件信息"]/text()')
        develop_company = parse(data, '//item[@name="开发商"]/text()')
        property_company = parse(data, '//item[@name="物业公司"]/text()')
        build_end_time = parse(data, '//phases/@t')
        html_info = data.decode().encode()
        crawler_time = datetime.datetime.now()
        info = {'comm_name': name, 'district': district, 'street': street, 'type': comm_type,
                'build_end_time': build_end_time, 'location': location, 'build_size': build_size,
                'land_size': land_size, 'green_rate': green_rate, 'volumetric_rate': volumetric_rate,
                'fee': fee, 'certificate': certificate, 'develop_company': develop_company,
                'property_company': property_company, 'city': cityname,'co_id':co_id,
                'kpdate':kpdate,'html_info':html_info,'crawler_time':crawler_time}
        collection.update_one({'co_id': co_id}, {'$set': info}, upsert=True)
        log.info('已更新小区={},info={}'.format(name, info))
    else:
        log.error('{}请求失败'.format(url))
        return


def parse(data, regx):
    result = etree.HTML(data.decode().encode())
    if len(result.xpath(regx)) == 0:
        return None
    else:
        return result.xpath(regx)[0]
