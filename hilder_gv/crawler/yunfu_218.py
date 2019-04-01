"""
url = http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid={B2FE0E00-F601-4748-9B9E-1475A3EF0085}&page=1
city : 云浮
CO_INDEX : 218
小区数量：
对应关系：f/t/t
"""

import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid={B2FE0E00-F601-4748-9B9E-1475A3EF0085}&page=1'
co_index = '218'
city = '云浮'
count = 0


class Yunfu(object):
    def __init__(self):
        self.headers = {
            'Referer': "http://www.yfci.gov.cn",
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.area_url = [
            ('云安区',
             'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid=4940be08-edc0-4792-a0b5-1ee518530651'),
            ('云浮市',
             'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid=b2fe0e00-f601-4748-9b9e-1475a3ef0085'),
            ('罗定市',
             'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid=71ffcc09-ac55-4960-be3c-56a7bbe06804'),
            ('郁南县',
             'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid=ded72eac-dd4f-4675-a044-301bf2b337a5'),
            ('新兴县',
             'http://www.yfci.gov.cn:8080/HousePresell/user_kfs_old.aspx?lid=bfb9bd7b-6468-469e-b3e7-e8498d6a2ecc'),
        ]

    def start_crawler(self):
        for url_city in self.area_url:
            area = url_city[0]
            response = requests.get(url_city[1], headers=self.headers)
            html = response.text
            page_str = re.search('id="pagetd".*?</td>', html, re.S | re.M).group()
            page = re.findall('href=".*?page=(.*?)"', page_str, re.S | re.M)[-1]
            for i in range(1, int(page) + 1):
                comm_url = url_city[1] + '&page=' + str(i)
                res = requests.get(comm_url, headers=self.headers)
                html_res = res.text
                comm_url_list = re.findall("href='(User_Presell_beian\.aspx\?.*?)'", html_res, re.S | re.M)
                for i in comm_url_list:
                    self.get_comm_info(i, area)

    def get_comm_info(self, comm_url, area):
        comm_url_ = 'http://www.yfci.gov.cn:8080/HousePresell/' + comm_url
        response = requests.get(comm_url_, headers=self.headers)
        html = response.text
        comm_detail_url_list = re.findall('href="(user_PresellInfo\.aspx\?FD=.*?)"', html, re.S | re.M)
        for i in comm_detail_url_list:
            self.get_comm_detail(i, area)

    def get_comm_detail(self, detail_url, area):
        try:
            comm = Comm(co_index)
            comm_detail_url = 'http://www.yfci.gov.cn:8080/HousePresell/' + detail_url
            response = requests.get(comm_detail_url, headers=self.headers)
            html = response.text
            comm.co_develops = re.search('id="kfsmc".*?<a.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_name = re.search('id="PresellName".*?<a.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_address = re.search('id="HouseRepose".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_build_size = re.search('id="PresellArea".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_all_house = re.search('id="djrqtd".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_land_use = re.search('id="landinfo".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_type = re.search('id="zczjtd".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_pre_sale = re.search('id="bookid".*?<a.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_pre_sale_date = re.search('id="FZDatebegin".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_open_time = re.search('id="kpdate".*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_id = re.search('FD=(.*?)&', detail_url, re.S | re.M).group(1)
            comm.area = area
            comm.insert_db()
            build_html = re.search('id="donglist".*?</table>', html, re.S | re.M).group()
            build_info_list = re.findall('<tr.*?</tr>', build_html, re.S | re.M)
            for i in build_info_list:
                build = Building(co_index)
                build.co_id = comm.co_id
                build.bu_address = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                build.bu_num = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                build.bu_floor = re.search('<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                build.bu_id = re.search("LID=(.*?)$", house_url, re.S | re.M).group(1)
                build.insert_db()
                self.get_house_info(house_url, comm.co_id, build.bu_id)
        except Exception as e:
            print('小区错误，co_index={},url={}'.format(co_index,comm_detail_url),e)

    def get_house_info(self, house_url, co_id, bu_id):
        try:
            house_url_ = 'http://www.yfci.gov.cn:8080/HousePresell/' + house_url
            response = requests.get(house_url_, headers=self.headers)
            html = response.text
            house_detail_url_list = re.findall('房屋号.*?href="(User_HouseInfo\.aspx\?ID=.*?)"', html, re.S | re.M)
            for i in house_detail_url_list:
                self.get_house_detail(i, co_id, bu_id)
        except Exception as e:
            print('房号错误，co_index={},url={}'.format(co_index, house_url_), e)

    def get_house_detail(self, house_detail_url, co_id, bu_id):
        try:
            house = House(co_index)
            house_detail_url_ = 'http://www.yfci.gov.cn:8080/HousePresell/' + house_detail_url
            response = requests.get(house_detail_url_, headers=self.headers)
            html = response.text
            if '找不到记录' in html:
                return
            house.ho_name = re.search('id="HouseNO".*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_true_size = re.search('id="HouseArea".*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_build_size = re.search('id="SumBuildArea1".*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_type = re.search('id="HouseUse".*?>(.*?)<', html, re.S | re.M).group(1)
            house.orientation = re.search('id="CHX".*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_type = re.search('id="CHX".*?>(.*?)<', html, re.S | re.M).group(1)
            house.co_id = co_id
            house.bu_id = bu_id
            house.insert_db()
        except Exception as e:
            print('房号错误，co_index={},url={}'.format(co_index, house_detail_url_), e)
