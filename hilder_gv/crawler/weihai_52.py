"""
url = http://221.2.144.162:8090/loupan_list.asp
city : 威海
CO_INDEX : 52
小区数量：
对应关系：
"""

import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://221.2.144.162:8090/loupan_list.asp?area=&name='
co_index = '52'
city = '威海'


class Weihai(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        for i in range(1, 47):
            try:
                index_url = 'http://221.2.144.162:8090/loupan_list.asp?Page=' + str(i)
                response = requests.get(index_url, headers=self.headers)
                html = response.content.decode('gbk')
                comm_url_list = re.findall('\[项目网站\] \[<a href=(.*?) target', html, re.S | re.M)
                self.get_comm_info(comm_url_list)
            except Exception as e:
                print("co_index={},翻页请求错误".format(co_index),e)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://221.2.144.162:8090/' + i
                response = requests.get(comm_url, headers=self.headers)
                html = response.content.decode('gbk')
                comm.co_id = re.search('id=(\d+)',i).group(1)
                comm.co_name = re.findall('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_develops = re.findall('开 发 商：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.area = re.findall('城 &nbsp;&nbsp;&nbsp;区：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_type = re.findall('物业类型：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_address = re.findall('物业位置：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_build_size = re.findall('建筑面积：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
                comm.insert_db()
                build_url_list = re.findall("height=20.*?<a href=(.*?) ", html, re.S | re.M)
                bu_pre_sale_list = re.findall("height=20.*?<Td>(.*?)<", html, re.S | re.M)
                self.get_build_info(build_url_list, bu_pre_sale_list, comm.co_name,comm.co_id)
            except Exception as e:
                print("co_index={},小区信息错误".format(co_index),e)

    def get_build_info(self, build_url_list, bu_pre_sale_list, co_name,co_id):
        for i in range(len(build_url_list)):
            try:
                build = Building(co_index)
                build.co_id = co_id

                build.co_name = co_name
                build.bu_pre_sale = bu_pre_sale_list[i]
                build.bu_id = re.search('lh=(\d+)',build_url_list[i]).group(1)
                build_url = 'http://221.2.144.162:8090/' + build_url_list[i]
                response = requests.get(build_url, headers=self.headers)
                html = response.content.decode('gbk')
                build.bu_num = re.findall('<font color=white.*?><b>(.*?)<', html, re.S | re.M)[0]
                build.bu_address = re.findall('坐落位置：</b>(.*?)<', html, re.S | re.M)[0]
                build.insert_db()
                ho_url_list = re.findall('background-.*?href=(.*?) ', html, re.S | re.M)
                ho_name_list = re.findall('background-color.*?<a.*?>(.*?)<', html, re.S | re.M)
                for i in range(len(ho_url_list)):
                    try:
                        house = House(co_index)
                        house_url = 'http://221.2.144.162:8090/' + ho_url_list[i]
                        result = requests.get(house_url, headers=self.headers).content.decode('gbk')
                        house.bu_id = build.bu_id
                        house.co_id = co_id
                        house.ho_type = re.findall('用&nbsp;&nbsp;&nbsp;途：.*?<td.*?>(.*?)<', result, re.S | re.M)[0]
                        house.ho_build_size = re.findall('建筑面积：.*?<td>(.*?)<', result, re.S | re.M)[0]
                        house.bu_num = build.bu_num
                        house.co_name = co_name
                        house.ho_name = ho_name_list[i]
                        house.insert_db()
                    except Exception as e:
                        print("co_index={},房屋信息错误".format(co_index),e)
            except Exception as e:
                print("co_index={},楼栋信息错误".format(co_index),e)
