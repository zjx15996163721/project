import requests
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
from lib.log import LogHandler
from lxml import etree
import time
import re
import json
log = LogHandler('yibin')
p = Proxies()
p = p.get_one(proxies_number=1)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['neijiang_json']
insert_collection = m['hilder_gv']['sichuan']


class NeiJiang:

    def __init__(self):
        self.headers = {
            'Cookie': 'ASP.NET_SessionId=vgameat4bhzse1315lbqulsm',
            'Host': '125.65.245.138',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.start_url = 'http://125.65.245.138/Client/Nanjiang/Scripts/Paging/PagingHandler.ashx'
        # ?MLandAgentName=&ProjectName=&ProjectAddress=&PrePressionCertNo=&&act=Project&columnID=&curPage=2&pageSize=20&rnd=0.0335846429727269

    def start_crawler(self):
        params = {
            # 'MLandAgentName': '',
            # 'ProjectName': '',
            # 'ProjectAddress': '',
            # 'PrePressionCertNo': '',
            'act': 'Project',
            # 'columnID': '',
            'curPage': '1',
            'pageSize': '400',
            # 'rnd': '0.0335846429727269',
        }
        r = requests.get(url=self.start_url, params=params, headers=self.headers)
        for i in r.json()['Records']:
            if not crawler_collection.find_one(i):
                crawler_collection.insert_one(i)
                log.info('插入一条数据{}'.format(i))
            else:
                log.info('重复数据')

    def get_house_info(self):
        for i in crawler_collection.find(no_cursor_timeout=True):
            ProjectName = i['ProjectName']
            TotalNumber = i['TotalNumber']
            ProjectAddress = i['ProjectAddress']
            ProjectId = i['ProjectId']
            url = 'http://125.65.245.138/Client/Nanjiang/Second/Detail/ProjectInfo/ProjectDetail.aspx'
            params = {
                'id': ProjectId,
                'RelationCID': '',
                'PageSize': '',
            }
            try:
                r = requests.get(url=url, params=params, headers=self.headers)
            except Exception as e:
                log.error(e)
                continue
            complete_time = re.search('计划竣工日期.*?</td>.*?>(.*?)</td>', r.text, re.S | re.M).group(1)
            region = re.search('所属片区.*?</td>.*?>(.*?)</td>', r.text, re.S | re.M).group(1)
            data = {
                'source': 'neijiang',
                'city': '内江',
                'region': region,
                'district_name': ProjectName,
                'complete_time': complete_time,
                'household_count': TotalNumber,
                'estate_charge': None,
                'address': ProjectAddress,
                'ProjectId': ProjectId
            }
            if not insert_collection.find_one({'source': 'neijiang', 'ProjectId': ProjectId}):
                insert_collection.insert_one(data)
                log.info('插入一条数据{}'.format(data))
            else:
                log.info('重复数据')


if __name__ == '__main__':
    n = NeiJiang()
    n.get_house_info()























