"""
url = http://www.fjnpfdc.com/House/ListCanSell
city : 南平
CO_INDEX : 32
小区数量：254
对应关系：小区：co_name 楼栋：bu_num
"""

import requests
from backup.producer import ProducerListUrl
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re

url = 'http://www.fjnpfdc.com/House/ListCanSell'
co_index = '32'
city = '南平'


class Nanping(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule=' 1/(.*?)页',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(int(page)):
            all_page_url = 'http://www.fjnpfdc.com/House/ListCanSell?page=' + str(i)
            response = requests.get(all_page_url)
            html = response.text
            comm_url_list = re.findall('<tr align="center">.*?<a href="(.*?)"', html, re.S | re.M)
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.fjnpfdc.com/House/' + i
                comm.co_develops = '公司名称：.*?<td.*?>(.*?)<'
                comm.co_pre_sale = '预售许可证：.*?<td.*?>(.*?)<'
                comm.co_name = '项目名称：.*?<td.*?>(.*?)<'
                comm.co_address = '项目坐落：.*?<td.*?>(.*?)<'
                comm.co_use = '规划用途：.*?<td.*?>(.*?)<'
                comm.co_build_size = '建筑面积：.*?<td.*?>(.*?)<'
                comm.co_id = 'ProjectId=(.*?)&'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='gbk',
                                    analyzer_rules_dict=comm.to_dict(),
                                    current_url_rule="<a href='(BuildingInfo.*?)'",
                                    analyzer_type='regex',
                                    headers=self.headers)
                build_url_list = p.get_details()
                self.get_build_info(build_url_list)
            except Exception as e:
                print("co_index={},小区{}错误".format(co_index,i),e)

    def get_build_info(self, build_url_list):
        for i in build_url_list:
            try:
                build = Building(co_index)
                build_url = 'http://www.fjnpfdc.com/House/' + i
                res = requests.get(build_url,headers=self.headers)
                con = res.content.decode('gbk')
                build.co_name = re.search("项目名称：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.bu_num = re.search("幢　　号：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.co_use = re.search("设计用途：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.co_build_structural = re.search("建筑结构：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.bu_floor = re.search("总 层 数：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.bu_build_size = re.search("总 面 积：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)
                build.co_build_end_time = re.search("竣工日期：.*?<td.*?>(.*?)<",con,re.S|re.M).group(1)

                house_url_list = re.findall('<a href="(HouseInfo.*?)"',con)
                # p = ProducerListUrl(page_url=build_url,
                #                     request_type='get', encode='gbk',
                #                     analyzer_rules_dict=build.to_dict(),
                #                     current_url_rule='<a href="(HouseInfo.*?)"',
                #                     analyzer_type='regex',
                #                     headers=self.headers)
                build.co_id = re.search('ProjectId=(.*?)&', i).group(1)
                build.bu_id = re.search('BuildingId=(.*?)&P', i).group(1)
                build.insert_db()
                # house_url_list = p.get_details()
                self.get_house_info(house_url_list,build.bu_id,build.co_id)
            except Exception as e:
                print("co_index={},楼栋{}错误".format(co_index,i),e)

    def get_house_info(self, house_url_list,bu_id,co_id):
        for i in house_url_list:
            try:
                house = House(co_index)
                house_url = 'http://www.fjnpfdc.com/House/' + i
                house_res = requests.get(house_url,headers=self.headers)
                house_con = house_res.content.decode('gbk')

                house.bu_id = bu_id
                house.co_id = co_id
                house.bu_num = re.search('幢　　号：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.ho_name = re.search('房　　号：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.co_name = re.search('项目名称：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.ho_build_size = re.search('建筑面积：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.ho_true_size = re.search('套内面积：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.ho_share_size = re.search('分摊面积：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)
                house.ho_floor = re.search('所 在 层：.*?<td>(.*?)<',house_con,re.S|re.M).group(1)

                house.insert_db()
            except Exception as e:
                print("co_index={},房屋{}错误".format(co_index,i),e)
