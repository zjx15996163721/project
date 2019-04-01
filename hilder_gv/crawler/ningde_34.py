"""
url = http://www.ndjsj.gov.cn/House/listproject
city : 宁德
CO_INDEX : 34
小区数量：838
对应关系：
        1、小区与楼栋：co_name
        2、楼栋与房号：bu_num
"""

import requests
from backup.producer import ProducerListUrl
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re

url = 'http://www.ndjsj.gov.cn/House/listproject'
co_index = '34'
city = '宁德'


class Ningde(object):
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
                       page_count_rule=' 1/(.*?)页',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(int(page)):
            all_page_url = url + '?page=' + str(i)
            response = requests.get(all_page_url, headers=self.headers)
            html = response.text
            comm_detail_url_list = re.findall('(/House/ProjectInfo\?ProjectId=.*?)"', html, re.S | re.M)
            self.get_comm_info(comm_detail_url_list)

    def get_comm_info(self, comm_detail_url_list):
        for i in comm_detail_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.ndjsj.gov.cn' + i
                comm.co_develops = '公司名称：.*?<td.*?>(.*?)<'
                comm.co_name = '项目名称：.*?<td.*?>(.*?)<'
                comm.co_pre_sale = '预售许可证：.*?<td.*?>(.*?)<'
                comm.co_address = '项目坐落：.*?<td.*?>(.*?)<'
                comm.co_use = '规划用途：.*?<td.*?>(.*?)<'
                comm.co_size = '占地面积：.*?<td.*?>(.*?)<'
                comm.co_build_size = '建筑面积：.*?<td.*?>(.*?)<'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=comm.to_dict(),
                                    current_url_rule="(BuildingInfo\?BuildingId=.*?)'",
                                    analyzer_type='regex',
                                    headers=self.headers)
                build_url_list = p.get_details()
                self.get_build_info(build_url_list)
            except Exception as e:
                print('宁德小区错误，url={}'.format(comm_url), e)

    def get_build_info(self, build_url_list):
        for i in build_url_list:
            try:
                build = Building(co_index)
                build_url = 'http://www.ndjsj.gov.cn/House/' + i
                build.co_name = '项目名称：.*?<td.*?>(.*?)<'
                build.bu_num = '幢　　号：.*?<td.*?>(.*?)<'
                build.bu_address = '坐落位置：.*?<td.*?>(.*?)<'
                build.co_build_structural = '建筑结构：.*?<td.*?>(.*?)<'
                build.bu_floor = '总 层 数：.*?<td.*?>(.*?)<'
                build.bu_build_size = '总 面 积：.*?<td.*?>(.*?)<'
                # build.bu_type = '设计用途：.*?<td.*?>(.*?)<'
                build.bu_all_house = '批准销售：.*?<td.*?>(.*?)<'
                p = ProducerListUrl(page_url=build_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=build.to_dict(),
                                    current_url_rule='javascript:ShowTitle.*?href="(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                house_url_list = p.get_details()
                self.get_house_info(house_url_list)
            except Exception as e:
                print('宁德楼栋错误,url={}'.format(build_url), e)

    def get_house_info(self, house_url_list):
        for i in house_url_list:
            try:
                house = House(co_index)
                house_url = 'http://www.ndjsj.gov.cn/House/' + i
                house.bu_num = '幢　　号：.*?<td.*?>(.*?)<'
                house.ho_name = '房　　号：.*?<td.*?>(.*?)<'
                house.co_name = '项目名称：.*?<td.*?>(.*?)<'
                house.ho_build_size = '建筑面积：.*?<td.*?>(.*?)<'
                house.ho_true_size = '套内面积：.*?<td.*?>(.*?)<'
                house.ho_share_size = '分摊面积：.*?<td.*?>(.*?)<'
                house.ho_type = '房屋用途：.*?<td.*?>(.*?)<'
                house.ho_floor = '所 在 层：.*?<td.*?>(.*?)<'
                house.ho_room_type = '房屋户型：.*?<td.*?>(.*?)<'
                p = ProducerListUrl(page_url=house_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=house.to_dict(),
                                    analyzer_type='regex',
                                    headers=self.headers)
                p.get_details()
            except Exception as e:
                print('宁德房号错误,url={}'.format(house_url), e)
