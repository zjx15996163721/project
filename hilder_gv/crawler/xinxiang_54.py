"""
url = http://web.xxfdc.gov.cn/onlineQuery/presaleQueryDetailList.do
city : 新乡
CO_INDEX : 54
小区数量：2818
对应关系：
"""

import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://web.xxfdc.gov.cn/onlineQuery/jsonPresaleQuery.do'
co_index = '54'
city = '新乡'


class Xinxiang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get('http://web.xxfdc.gov.cn/onlineQuery/jsonPresaleQuery.do', headers=self.headers)
        html = response.text
        comm_id_list = re.findall('"id":"(.*?)"', html, re.S | re.M)
        self.get_comm_info(comm_id_list)

    def get_comm_info(self, comm_id_list):
        for i in comm_id_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://web.xxfdc.gov.cn/onlineQuery/projectInformation.do?xmId=' + i
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.search('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('项目地址：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_develops = re.search('开发商：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_all_house = re.search('已售总套数：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('已售总面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('行政区别：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_volumetric = re.search('容积率：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_id = i
                comm.insert_db()
                bu_html = re.search('<table class="table table-bordered itemInfoDetail.*?</table>', html,
                                    re.S | re.M).group()
                build_info_list = re.findall('<tr>.*?</tr>', bu_html, re.S | re.M)[1:]
                for i in build_info_list:
                    try:
                        build = Building(co_index)
                        build.bu_num = re.search('<td>(.*?)<', i, re.S | re.M).group(1)
                        build.bu_all_house = re.search('<td>.*?<td>.*?<td>(.*?)<', i, re.S | re.M).group(1)
                        build.bu_id = re.search('buildId=(.*?)&', i, re.S | re.M).group(1)
                        build.co_id = comm.co_id
                        build.insert_db()
                        house_url = re.search('<a href="(.*?)"', bu_html, re.S | re.M).group(1)
                        response = requests.get(house_url, headers=self.headers)
                        html = response.text
                        house_url_list = re.findall('<td width="110">.*?<a.*?href="(.*?)"', html, re.S | re.M)
                        self.get_house_info(house_url_list, build.bu_id, comm.co_id)
                    except Exception as e:
                        print('楼栋错误，co_index={},url={}'.format(co_index, house_url), e)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_house_info(self, house_url_list, bu_id, co_id):
        for i in house_url_list:
            try:
                house = House(co_index)
                response = requests.get(i, headers=self.headers)
                html = response.text
                house.ho_name = re.search('门牌号：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_floor = re.search('所在层：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_type = re.search('房屋性质：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('预测建筑面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_true_size = re.search('预测套内面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_share_size = re.search('预测分摊面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.co_address = re.search('房屋坐落：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                house.bu_id = bu_id
                house.co_id = co_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, i), e)
