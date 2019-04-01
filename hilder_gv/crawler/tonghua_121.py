"""
url = http://thfdc.net/
city : 通化
CO_INDEX : 121
小区数量：
对应关系：f/t/t
"""

import requests
from backup.comm_info import Building, House
import re

url = 'http://thfdc.net/'
co_index = '121'
city = '通化'
count = 0


class Tonghua(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        html = response.text
        paper = re.search('<MARQUEE(.*?)</MARQUEE>', html, re.S | re.M).group(1)
        comm_info_list = re.findall(r'<tr   >(.*?)</tr>', paper, re.S | re.M)
        self.get_comm_info(comm_info_list)

    def get_comm_info(self, comm_info_list):
        for i in comm_info_list:
            build = Building(co_index)
            house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
            build.bu_num = re.search('<a.*?>(.*?)<', i, re.S | re.M).group(1)
            build.bu_address = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
            build.bu_pre_sale = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
            build.bu_id = re.search('slbh=(.*?)&', i, re.S | re.M).group(1)
            build.insert_db()
            self.get_house_info(house_url, build.bu_id)

    def get_house_info(self, house_url, bu_id):
        response = requests.get('http://thfdc.net/' + house_url, headers=self.headers)
        html = response.text
        house_info_list = re.findall('<tr onClick=.*?</tr>', html, re.S | re.M)
        for i in house_info_list:
            try:
                house = House(co_index)
                house.ho_name = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                house.area = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                house.ho_build_size = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                house.ho_type = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                house.bu_id = bu_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format())
