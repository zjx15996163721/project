"""
url = http://58.51.240.121:8503/More_xm.aspx
city : 黄石
CO_INDEX : 213
小区数量：
对应关系：
"""
import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://58.51.240.121:8503/More_xm.aspx'
co_index = '213'
city = '黄石'
count = 0


class Huangshi(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        html = response.text
        page = re.search('下一页</a>.*?page=(.*?)"', html, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            try:
                page_url = 'http://58.51.240.121:8503/More_xm.aspx?page=' + str(i)
                res = requests.get(page_url, headers=self.headers)
                paper = res.text
                paper_comm = re.search('<b>项目名称</b>.*?</table>', paper, re.S | re.M).group()
                comm_url_list = re.findall('<a href="(Pub_lpxx.*?)".*?<td.*?<td.*?>(.*?)<', paper_comm, re.S | re.M)
                self.get_comm_info(comm_url_list)
            except Exception as e:
                print('请求错误，co_index={},url={}'.format(co_index, page_url), e)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm.co_id = re.search('DevProjectId=(.*?)$', i[0]).group(1)
                comm.area = i[1]
                comm_url = 'http://58.51.240.121:8503/' + i[0]
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.search('id="ProjectInfo1_lblProjectName">(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('id="ProjectInfo1_lblProjectAddress">(.*?)<', html, re.S | re.M).group(1)
                comm.co_develops = re.search('id="ProjectInfo1_lblCorpName">(.*?)<', html, re.S | re.M).group(1)
                comm.co_type = re.search('id="ProjectInfo1_lblProjectType">(.*?)<', html, re.S | re.M).group(1)
                comm.co_size = re.search('id="ProjectInfo1_lblXmzgm">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_start_time = re.search('id="ProjectInfo1_lblJhkgrq">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('id="ProjectInfo1_lblZjzmj">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_end_time = re.search('id="ProjectInfo1_lblJhjfsyrq">(.*?)<', html, re.S | re.M).group(1)
                comm.co_volumetric = re.search('id="ProjectInfo1_lblRjl">(.*?)<', html, re.S | re.M).group(1)
                comm.co_green = re.search('id="ProjectInfo1_lblJdl">(.*?)<', html, re.S | re.M).group(1)
                build_url_list = re.findall('href="(Pub_ysxx\.aspx\?PresellId=.*?)"', html, re.S | re.M)
                self.get_build_info(build_url_list, comm)
            except Exception as e:
                print('请求错误，co_index={}，url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url_list, comm):
        for i in build_url_list:
            try:
                build_url = 'http://58.51.240.121:8503/' + i
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                comm.co_pre_sale = re.search('id="PresellInfo1_lblXkzh">(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale_date = re.search('id="PresellInfo1_lblFzrq">(.*?)<', html, re.S | re.M).group(1)
                comm.insert_db()
                build_info_list = re.findall('<tr bgcolor="#FFFFFF">.*?</tr>', html, re.S | re.M)
                for i in build_info_list:
                    build = Building(co_index)
                    build.co_id = comm.co_id
                    build.bu_num = re.search('<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_floor = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_all_house = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_id = re.search('PresellId=(.*?)$', build_url).group(1)
                    build.insert_db()
                    house_url = re.search('a href="(.*?)"', i, re.S | re.M).group(1)
                    self.get_house_info(house_url, comm.co_id, build.bu_id)
            except Exception as e:
                print('请求错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_info(self, house_url, co_id, bu_id):
        house_url_ = 'http://58.51.240.121:8503/' + house_url
        try:
            response = requests.get(house_url_, headers=self.headers)
            html = response.text
            house_info_list = re.findall('getMoreHouseInfo.*?</table>', html, re.S | re.M)[1:]
            for i in house_info_list:
                house = House(co_index)
                house.co_id = co_id
                house.bu_id = bu_id
                house.ho_name = re.search('>(.*?)<', i, re.S | re.M).group(1)
                house.ho_type = re.search('性质&nbsp;(.*?)<', i, re.S | re.M).group(1)
                house.ho_build_size = re.search('面积&nbsp;(.*?)<', i, re.S | re.M).group(1)
                house.co_build_structural = re.search('结构&nbsp;(.*?)<', i, re.S | re.M).group(1)
                house.insert_db()
        except Exception as e:
            print('请求错误，co_index={},url={}'.format(co_index, house_url_), e)
