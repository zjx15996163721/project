"""
url = http://www.xyfcj.com/html/jplp/index.html
city : 新余
CO_INDEX : 55
小区数量：
对应关系：
    小区与楼栋：co_id
    楼栋与房屋：bu_id
"""

import requests
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re

url = 'http://www.xyfcj.com/html/jplp/index.html'
co_index = '55'
city = '新余'

count = 0


class Xinyu(object):
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
                       page_count_rule='共(.*?)页',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            if i is 1:
                all_page_url = 'http://www.xyfcj.com/html/jplp/index.html'
            else:
                all_page_url = 'http://www.xyfcj.com/html/jplp/index_' + str(i) + '.html'
            response = requests.get(all_page_url, headers=self.headers)
            html = response.text
            comm_url_list = re.findall('<a style="COLOR: #000000" target="_blank" href="(.*?)"', html, re.S | re.M)
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                response = requests.get(i, headers=self.headers)
                html = response.text
                comm = Comm(co_index)
                comm.co_name = re.findall('PROJECT_XMMC">(.*?)<', html, re.S | re.M)[0]
                comm.co_develops = re.findall('PROJECT_KFQY_NAME">(.*?)<', html, re.S | re.M)[0]
                comm.co_address = re.findall('PROJECT_XMDZ">(.*?)<', html, re.S | re.M)[0]
                comm.area = re.findall('PROJECT_SZQY">(.*?)<', html, re.S | re.M)[0]
                comm.co_volumetric = re.findall('PROJECT_RJL">(.*?)<', html, re.S | re.M)[0]
                comm.co_build_size = re.findall('PROJECT_GHZJZMJ">(.*?)<', html, re.S | re.M)[0]
                comm.co_pre_sale = re.findall('YSXKZH">(.*?)<', html, re.S | re.M)[0]
                comm.co_id = re.findall('PROJECT_XMBH">(.*?)<', html, re.S | re.M)[0]
                comm.insert_db()
                global count
                count += 1
                print(count)
                bu_info = re.search('id="buildInfo".*?value="(.*?)"', html, re.S | re.M).group(1)
                self.get_build_info(bu_info, comm.co_id, i)
            except Exception as e:
                print('小区错误,co_index={},url={}'.format(co_index, i), e)

    def get_build_info(self, bu_info, co_id, build_url):
        build_list = bu_info.split(';;')
        for i in build_list:
            try:
                build = Building(co_index)
                bu_code_list = i.split(',,')
                build.bu_num = bu_code_list[1]
                build.bu_id = bu_code_list[0]
                build.co_id = co_id
                build.insert_db()
                self.get_house_info(build.bu_id, co_id)
            except Exception as e:
                print('楼栋错误,co_index={},url={}'.format(co_index, build_url), e)

    def get_house_info(self, bu_id, co_id):
        house_url = "http://www.xyfdc.gov.cn/wsba/Common/Agents/ExeFunCommon.aspx"
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.Wsba.CBuildTableEx.GetBuildHTMLEx\">\r\n<item>" + \
                  bu_id + "</item>\r\n<item>1</item>\r\n<item>1</item>\r\n<item>80</item>\r\n<item>840</item>\r\n<item>g_oBuildTable</item>\r\n<item> 1=1</item>\r\n<item>1</item>\r\n<item>false</item>\r\n</param>\r\n"
        headers = {
            'Content-Type': "text/xml",
        }
        response = requests.request("POST", house_url, data=payload, headers=headers)
        html = response.text
        house_info_list = re.findall("onclick=.g_oBuildTable.clickRoom.*? title='(.*?)'", html, re.S | re.M)
        for i in house_info_list:
            try:
                house = House(co_index)
                house.ho_name = re.search('房号：(.*?)单元：', i, re.S | re.M).group(1)
                house.ho_build_size = re.search('总面积：(.*?)平方米', i, re.S | re.M).group(1)
                house.ho_type = re.search('用途：(.*?)户型', i, re.S | re.M).group(1)
                house.ho_room_type = re.search('户型：(.*?)状态', i, re.S | re.M).group(1)
                house.info = i
                house.bu_id = bu_id
                house.co_id = co_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={},data={}'.format(co_index, house_url, payload), e)
