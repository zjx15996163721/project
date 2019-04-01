"""
url = http://219.154.46.179:16666/Client/Nanjiang/Second/Second_HouseManger.aspx?RelationCID=2&PageSize=10
city : 安阳
CO_INDEX : 99
小区数量：
"""

import requests
from backup.comm_info import Comm, Building, House
import re, json

url = 'http://219.154.46.179:16666/Client/Nanjiang/Scripts/Paging/PagingHandler.ashx?MLandAgentName=&ProjectName=&ProjectAddress=&PrePressionCertNo=&&act=Project&columnID=2&curPage=1&pageSize=10000&rnd=0.03583054265358743'
co_index = '99'
city = '安阳'


class Anyang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url=url, headers=self.headers)
        comm_list = response.json()['Records']
        for i in comm_list:
            co_id = i['ProjectId']
            comm_detail_url = 'http://219.154.46.179:16666/Client/Nanjiang/Second/Detail/ProjectInfo/ProjectDetail.aspx?id=' + co_id
            self.get_comm_detail(comm_detail_url, co_id)

    def get_comm_detail(self, comm_detail_url, co_id):
        comm = Comm(co_index)
        try:
            response = requests.get(comm_detail_url, headers=self.headers)
            html = response.text
            comm.co_name = re.search('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_type = re.search('项目主体性质：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_develops = re.search('主开发商：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_address = re.search('项目建设地址：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_all_size = re.search('项目总规划面积（㎡）：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_build_start_time = re.search('计划开工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_build_end_time = re.search('计划竣工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_id = co_id
            comm.insert_db()
            build_info_list = re.findall('id="lpan".*?</tr>', html, re.S | re.M)
            self.get_build_info(build_info_list, co_id)
        except Exception as e:
            print('小区错误，co_index={},url={}'.format(co_index, comm_detail_url), e)

    def get_build_info(self, build_info_list, co_id):
        for i in build_info_list:
            try:
                build = Building(co_index)
                build.bu_num = re.search('<td>(.*?)</td>', i, re.S | re.M).group(1)
                build.bu_all_house = re.search('<td>.*?<td>(.*?)</td>', i, re.S | re.M).group(1)
                build.bu_all_size = re.search('<td>.*?<td>.*?<td>(.*?)</td>', i, re.S | re.M).group(1)
                build.bu_id = re.search('\?id=(.*?)"', i, re.S | re.M).group(1)
                build.co_id = co_id
                build.insert_db()
                house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                self.get_house_info(house_url, co_id, build.bu_id)
            except Exception as e:
                print('楼栋错误，co_index={},str={}'.format(co_index, i), e)

    def get_house_info(self, house_url, co_id, bu_id):
        response = requests.get(house_url)
        html = response.text
        info = re.search('var houselist =.*?eval\((.*?)\);', html, re.S | re.M).group(1)
        data_list = json.loads(info)
        for data in data_list:
            try:
                house = House(co_index)
                house.ho_name = data['HouseName']
                house.unit = data['UnitName']
                house.co_build_structural = data['StruTypeName']
                house.ho_build_size = data['PreBuildArea']
                house.ho_true_size = data['PreInnerArea']
                house.ho_share_size = data['PreApportionArea']
                house.ho_floor = data['FloorName']
                house.ho_type = data['LayoutTypeName']
                house.co_id = co_id
                house.bu_id = bu_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_url), e)
