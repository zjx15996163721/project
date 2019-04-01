"""
url = http://125.65.245.138/Client/Nanjiang/Second/Second_HouseManger.aspx
city : 内江
CO_INDEX : 151
小区数量：
对应关系：
"""

import requests
from backup.comm_info import Comm
import re

url = 'http://125.65.245.138/Client/Nanjiang/Scripts/Paging/PagingHandler.ashx?MLandAgentName=&ProjectName=&ProjectAddress=&PrePressionCertNo=&&act=Project&curPage=1&pageSize=10000'
co_index = '219'
city = '内江'
count = 0


class Neijiang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        comm_list = response.json()['Records']
        for i in comm_list:
            co_id = i['ProjectId']
            comm_url = 'http://125.65.245.138/Client/Nanjiang/Second/Detail/ProjectInfo/ProjectDetail.aspx?id=' + str(
                co_id)
            self.get_comm_info(comm_url, co_id)

    def get_comm_info(self, comm_url, co_id):
        comm = Comm(co_index)
        response = requests.get(comm_url, headers=self.headers)
        html = response.text
        comm.co_name = re.search('项目名称：.*?class="left">(.*?)</td>', html, re.S | re.M).group(1)
        comm.co_develops = re.search('主开发商：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_address = re.search('项目建设地址：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_build_size = re.search('项目总规划面积（㎡）：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_build_start_time = re.search('计划开工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_build_end_time = re.search('计划竣工日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.area = re.search('所属片区：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_size = re.search('占地面积（㎡）：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.co_id = co_id
        comm.insert_db()
