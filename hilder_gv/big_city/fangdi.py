import requests
from lxml import etree
from pymongo import MongoClient
import re
from lib.log import LogHandler
import json
import threading
log = LogHandler('fangdi')

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['fangdi']


class FangDi:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        }
        self.start_url = 'http://www.fangdi.com.cn/service/freshHouse/getHosueList.action'
        self.area_list = [
            '27d3af3bd45acf5e',
            'c3243f2018413f06',
            '53c7b05ea45cf006',
            'c25cb8e534080b41',
            '3e9d0ed5cf865b9b',
            '9999a061b2bf2968',
            'dc24b8a987de1555',
            'e153da3d0ca1946e',
            '5560708b21685990',
            '2385fa574f10a564',
            'e5cf885d0ef25e94',
            'd095fa89de83a452',
            '5391be55e75e5506',
            '5591ec7dfc0c3b7b',
            '45c69c52e212e98d',
            'c3a04b33d3238385',
            '1c1f50e015c71814',
            'ef8c008816798859',
            'd6ff877c62587d67',
        ]

    def start_crawler(self):
        for districtID in self.area_list:
            params = {
                'districtID': districtID,
                'dicRegionID': '',
                'stateID': '',
                'houseAreaID': 0,
                'dicAvgpriceID': 0,
                'dicPositionID': 0,
                'houseTypeID': '27d3af3bd45acf5e',
                'address': '',
                'openingID': '',
                'projectName': '',
                'currentPage': 1,
            }
            try:
                r = requests.post(url=self.start_url, params=params, headers=self.headers)
            except Exception as e:
                print(e)
                continue
            total_page = re.search('共.*?(\d+).*?页', r.text, re.S | re.M).group(1)
            print(total_page)
            self.get_page_url(total_page, districtID)

    def get_page_url(self, total_page, districtID):
        for page in range(1, int(total_page)+1):
            params = {
                'districtID': districtID,
                'dicRegionID': '',
                'stateID': '',
                'houseAreaID': 0,
                'dicAvgpriceID': 0,
                'dicPositionID': 0,
                'houseTypeID': '27d3af3bd45acf5e',
                'address': '',
                'openingID': '',
                'projectName': '',
                'currentPage': page,
            }
            try:
                r = requests.post(url=self.start_url, params=params, headers=self.headers)
            except Exception as e:
                print(e)
                continue
            text = r.json()['htmlView']
            tree = etree.HTML(text)
            info_list = tree.xpath('//tr[@class="default_row_tr"]')
            for info in info_list:
                name = info.xpath('./td[2]/a/text()')[0]
                try:
                    address = info.xpath('./td[3]/text()')[0]
                except:
                    address = None
                try:
                    household_count = info.xpath('./td[4]/text()')[0]
                except:
                    household_count = None
                try:
                    area = info.xpath('./td[5]/text()')[0]
                except:
                    area = None
                region = info.xpath('./td[6]/text()')[0]
                data = {
                    'estate_type2': '普通住宅',
                    'city': '上海',
                    'region': region,
                    'district_name': name,
                    'address': address,
                    'household_count': household_count,
                    'area': area,
                }
                if not collection.find_one({'city': '上海',
                                            'region': region,
                                            'district_name': name,
                                            'household_count': household_count,
                                            'estate_type2': '普通住宅',
                                            'address': address,
                                            'area': area}):
                    collection.insert_one(data)
                    log.info('插入一条数据{}'.format(data))
                else:
                    log.info('重复数据')


if __name__ == '__main__':
    fangdi = FangDi()
    fangdi.start_crawler()





