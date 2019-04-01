"""
url = http://222.223.160.199:8088/website/buildquery/mapData.jsp
city : 张家口
CO_INDEX : 211
小区数量：
对应关系： f/t/t
"""

import requests
from backup.comm_info import Building, House
import re

url = 'http://222.223.160.199:8088/website/buildquery/mapData.jsp'
co_index = '211'
city = '张家口'
count = 0


class Zhangjiakou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        html = response.text
        page = re.search('第1/(.*?)页', html, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            try:
                page_url = 'http://222.223.160.199:8088/website/buildquery/mapData.jsp?CurPage=' + str(page)
                res = requests.get(page_url, headers=self.headers)
                paper = res.text
                build_url_list = re.findall('onclick=.viewBuild\((.*?)\).*?viewHouse\((.*?)\)', paper, re.S | re.M)
                self.get_build_info(build_url_list)
            except Exception as e:
                print('请求错误，url={}'.format(page_url),e)

    def get_build_info(self, build_url_list):
        for i in build_url_list:
            try:
                build = Building(co_index)
                build_url = 'http://222.223.160.199:8088/website/buildquery/selectBuild.jsp?buildID=' + i[0]
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                build.bu_id = i[0]
                build.co_build_structural = re.search('结构类型.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bo_build_end_time = re.search('建成年份.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_build_size = re.search('总建筑面积.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_num = re.search('幢号.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.size = re.search('占地面积.*?<td>(.*?)<', html, re.S | re.M).group(1)
                build.bu_floor = re.search('房屋层数.*?<td>(.*?)<', html, re.S | re.M).group(1)
                build.bu_all_house = re.search('房屋套数.*?<td>(.*?)<', html, re.S | re.M).group(1)
                build.area = re.search('坐落区.*?<td>(.*?)<', html, re.S | re.M).group(1)
                build.insert_db()
                self.get_house_info(build.bu_id)
            except Exception as e:
                print('请求错误，url={}'.format(build_url),e)

    def get_house_info(self, bu_id):
        try:
            house_url = 'http://222.223.160.199:8088/website/buildquery/selectHouse.jsp?buildID=' + bu_id
            response = requests.get(house_url, headers=self.headers)
            html = response.text
            house_id_list = re.findall('ondblclick="selectdata\((.*?)\)', html, re.S | re.M)
            for i in house_id_list:
                self.get_house_detail(i, bu_id)
        except Exception as e:
            print('请求错误，url={}'.format(house_url), e)

    def get_house_detail(self, house_id, bu_id):
        try:
            house = House(co_index)
            detail_url = 'http://222.223.160.199:8088/website/Hutu?id=' + house_id
            response = requests.get(detail_url, headers=self.headers)
            html = response.text
            house.ho_floor = re.search('层号.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.ho_build_size = re.search('总面积.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.ho_share_size = re.search('分摊面积.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.ho_true_size = re.search('套内面积.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.ho_type = re.search('房屋用途.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.ho_floor = re.search('层号.*?value="(.*?)"', html, re.S | re.M).group(1)
            house.bu_id = bu_id
            house.insert_db()
        except Exception as e:
            print('请求错误，url={}'.format(detail_url), e)