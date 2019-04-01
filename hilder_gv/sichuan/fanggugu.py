import requests
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
from retry import retry

log = LogHandler('fanggugu')
p = Proxies()
p = p.get_one(proxies_number=1)

client = MongoClient(host='192.168.0.105', port=27018)
db = client.fangjia_craw
db.authenticate('developer', 'goojia@123456')
collection = db['third_party_price']

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['sichuan']


class FangGuGu:

    def __init__(self):
        self.headers = {
            'Cookie': 'jrbqiantai=CD7D4B8BAC54F4727CD50D6B87456BAC; Hm_lvt_203904e114edfe3e6ab6bc0bc04207cd=1545792569; loginCity_JR_8a2db3a967aa1f990167d0017f7d5da7=%u5317%u4EAC; Hm_lpvt_203904e114edfe3e6ab6bc0bc04207cd=1545792608',
            'Host': 'www.fungugu.com',
            'Origin': 'http://www.fungugu.com',
            'Referer': 'http://www.fungugu.com/JinRongGuZhi/toJinRongGuZhiFromHome?xqmc=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&gjdx=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&residentialName=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&realName=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&dz=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&xzq=%E9%94%A1%E5%B1%B1%E5%8C%BA&xqid=16595&ldid=&dyid=&hid=&loudong=&danyuan=&hu=&retrievalMethod=%E6%99%AE%E9%80%9A%E6%A3%80%E7%B4%A2&originalInputItem=%E6%9F%8F%E5%BA%84%E4%B8%80%E6%9D%91&address=&source=&guid=af623b8a-5876-11e5-91e1-1051721bd1a9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.city = ["成都", "绵阳", "宜宾", "自贡", "攀枝花", "广元", "乐山", "南充", "泸州", "资阳", "内江", "达州", "巴中", "遂宁", "眉山", "德阳",
                    "广安", "雅安", "阿坝州", "甘孜州", "凉山州"]

    def start_crawler(self):
        for city in self.city:
            for data in collection.find({"s_date": 201810, "source": "房估估", "city": city}, no_cursor_timeout=True):
                residentialAreaId = re.search('.*?AreaID=(\d+)', data['url'], re.S | re.M).group(1)
                city = data['city']
                info = {
                    'residentialAreaId': residentialAreaId,
                    'name': data['name'],
                    'region': data['region']
                }
                self.start_request(info, city)

    def start_request(self, info, city):
        url = 'http://www.fungugu.com/JinRongGuZhi/getBaseinfo'
        data = {
            'residentialAreaId': info['residentialAreaId'],
            'city': city
        }
        # try:
        #     r = requests.post(url=url, data=data, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error('请求失败　url={}, e={}'.format(url, e))
        #     return
        r = self.send_url(url=url,data=data)
        try:
            data_list = r.json()['json'][0]
        except Exception as e:
            log.error('无法序列化　url={}, e={}'.format(url, e))
            return
        try:
            estate_charge = data_list['residentialareaMap']['managementFees']
        except:
            estate_charge = None
        try:
            address = data_list['residentialareaMap']['address']
        except:
            address = None
        data = {
            'source': '房估估',
            'city': city,
            'region': info['region'],
            'district_name': info['name'],
            'complete_time': None,
            'household_count': None,
            'estate_charge': estate_charge,
            'address': address,
            'estate_type2': '普通住宅',
        }
        if not crawler_collection.find_one(
                {'source': '房估估', 'city': city, 'region': info['region'], 'district_name': info['name'],
                 'household_count': None, 'estate_charge': estate_charge, 'address': address}):
            crawler_collection.insert_one(data)
            # log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')

    @retry(delay=2,logger=log)
    def send_url(self,url,data):
        res = requests.post(url=url, data=data, headers=self.headers, proxies=p)
        return res


if __name__ == '__main__':
    fanggugu = FangGuGu()
    fanggugu.start_crawler()
