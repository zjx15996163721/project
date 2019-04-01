"""
url = http://www.fjlyfdc.com.cn/House/Link/YSXXCX.cshtml
city : 龙岩
CO_INDEX : 138
小区数量：
"""

import requests
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re

url = 'http://www.fjlyfdc.com.cn/House/Link/YSXXCX.cshtml'
co_index = '138'
city = '龙岩'


class Longyan(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='1/(.*?)页',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(0, int(page) + 1):
            page_url = 'http://www.fjlyfdc.com.cn/House/Link/YSXXCX.cshtml?pagenumber=' + str(i)
            response = requests.get(page_url)
            html = response.text
            comm_url_list = re.findall('class="c".*?href="(.*?)"', html, re.S | re.M)
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm_url = 'http://www.fjlyfdc.com.cn/' + i
            try:
                comm = Comm(co_index)
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_develops = re.search('公司名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_name = re.search('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale = re.search('预售许可证：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('项目坐落：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_type = re.search('规划用途：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('建筑面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_volumetric = re.search('容积率：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_green = re.search('绿地率：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_open_time = re.search('开工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_end_time = re.search('竣工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_all_house = re.search('批准销售：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_all_size = re.search('批准销售：.*?<td.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_id = re.search('CaseId=(.*?)$', comm_url).group(1)
                comm.insert_db()
                build_url_list = re.findall('href="(/House/BuildingInfo\?buildingInfoID=.*?&amp;caseID=.*?)"', html,
                                            re.S | re.M)
                self.get_build_info(build_url_list, comm.co_id)
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url_list, co_id):
        for i in build_url_list:
            build_url = 'http://www.fjlyfdc.com.cn/' + i
            try:
                build = Building(co_index)
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                build.bu_id = re.search('buildingInfoID=(.*?)&', build_url).group(1)
                build.co_id = co_id
                build.bo_develops = re.search('开发商：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.co_name = re.search('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_address = re.search('坐落位置：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_num = re.search('幢号：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.co_build_structural = re.search('建筑结构：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_type = re.search('设计用途：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_floor = re.search('总 层 数：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.co_all_size = re.search('总面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bo_build_start_time = re.search('开工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.insert_db()
                house_url_list = re.findall('href="(/House/HouseInfo\?HouseCenterID=.*?)"', html, re.S | re.M)
                self.get_house_info(house_url_list, build.bu_id, co_id)
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_info(self, house_url_list, bu_id, co_id):
        for i in house_url_list:
            house_url = 'http://www.fjlyfdc.com.cn/' + i
            try:
                response = requests.get(house_url, headers=self.headers)
                html = response.text
                house = House(co_index)
                house.bu_id = bu_id
                house.co_id = co_id
                house.ho_name = re.search('房　　号：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('建筑面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_true_size = re.search('套内面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_share_size = re.search('分摊面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_floor = re.search('所 在 层：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_url), e)
