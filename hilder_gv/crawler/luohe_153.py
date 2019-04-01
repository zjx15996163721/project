"""
url = http://www.lhfdc.gov.cn/Templets/LH/aspx/HPMS/ProjectList.aspx
city : 漯河
CO_INDEX : 153
小区数量：
对应关系：
"""

import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
import re

url = 'http://www.lhfdc.gov.cn/Templets/LH/aspx/HPMS/ProjectList.aspx'
co_index = '153'
city = '漯河'
count = 0


class Luohe(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        all_comm_url_list = []
        response = requests.get(url=url, headers=self.headers)
        html = response.text
        comm_url_code_list = re.findall("target=._self. href='.*?code=(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url_code_list
        data = self.get_view_state(html)
        comm_list = self.get_all_url_comm(data, 0, all_comm_url_list)
        print(comm_list)
        self.get_comm_info(comm_list)

    def get_comm_info(self, comm_list):
        for i in comm_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.lhfdc.gov.cn/templets/lh/aspx/hpms/ProjectInfo.aspx?code=' + str(i)
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.search('id="PROJECT_XMMC1">(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('id="PROJECT_XMDZ">(.*?)<', html, re.S | re.M).group(1)
                comm.co_develops = re.search('id="PROJECT_KFQY_NAME1">(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('id="PROJECT_SZQY">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('id="PROJECT_GHZJZMJ">(.*?)<', html, re.S | re.M).group(1)
                comm.co_volumetric = re.search('id="PROJECT_RJL">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_start_time = re.search('id="PROJECT_JHKGRQ">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_end_time = re.search('id="PROJECT_JHJGRQ">(.*?)<', html, re.S | re.M).group(1)
                house_all = re.search('id="lbYsZZTs">(.*?)<', html, re.S | re.M).group(1)
                house_all_a = re.search('id="lbWsZZTs">(.*?)<', html, re.S | re.M).group(1)
                bus_all = re.search('id="lbWsSYTs">(.*?)<', html, re.S | re.M).group(1)
                bus_all_a = re.search('id="lbYsSYTs">(.*?)<', html, re.S | re.M).group(1)
                comm.co_all_house = int(house_all_a) + int(house_all) + int(bus_all) + int(bus_all_a)
                area_size_a = re.search('id="lbYsZZMj">(.*?)<', html, re.S | re.M).group(1)
                area_size_b = re.search('id="lbWsZZMj">(.*?)<', html, re.S | re.M).group(1)
                area_size_c = re.search('id="lbWsSYMj">(.*?)<', html, re.S | re.M).group(1)
                area_size_d = re.search('id="lbYsSYMj">(.*?)<', html, re.S | re.M).group(1)
                comm.co_size = float(area_size_a) + float(area_size_b) + float(area_size_c) + float(area_size_d)
                comm.co_id = str(i)
                comm.insert_db()
                self.get_build_info(comm.co_id)
            except Exception as e:
                print('小区 错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, co_id):
        build_url = 'http://www.lhfdc.gov.cn/Templets/LH/aspx/HPMS/GetQueryResult.ashx?type=0&PCODE=' + co_id
        response = requests.get(build_url, headers=self.headers)
        html = response.text
        build_list = re.findall("bid=(.*?) .*?onclick=\"BuildChange\(.*?,'(.*?)','(.*?)'\)", html, re.S | re.M)
        for i in build_list:
            try:
                build = Building(co_index)
                build.co_id = co_id
                build.bu_pre_sale = i[1]
                build.bu_num = i[2]
                build.bu_id = i[0]
                build.insert_db()
                self.get_house_info(co_id, build.bu_id)
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_info(self, co_id, bu_id):
        house_url = "http://www.lhfdc.gov.cn/Common/Agents/ExeFunCommon.aspx"
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.Wsba2.CBuildTable.GetPublicHTML\">\r\n<item>" + bu_id + "</item>\r\n<item> 1=1</item>\r\n</param>"
        headers = {
            'Content-Type': "text/xml",
        }
        response = requests.post(house_url, data=payload, headers=headers)
        html = response.text
        house_url_list = re.findall('<a href="RoomInfo\.aspx\?code=(.*?)".*?<a', html, re.S | re.M)
        self.get_house_detail(house_url_list, bu_id, co_id)

    def get_house_detail(self, house_url_list, bu_id, co_id):
        for i in house_url_list:
            try:
                house = House(co_index)
                house_detail_url = 'http://www.lhfdc.gov.cn/templets/lh/aspx/hpms/RoomInfo.aspx?code=' + i
                response = requests.get(house_detail_url, headers=self.headers)
                html = response.text
                house.ho_name = re.search('id="ROOM_ROOMNO">(.*?)<', html, re.S | re.M).group(1)
                house.ho_room_type = re.search('id="ROOM_FWHX">(.*?)<', html, re.S | re.M).group(1)
                house.ho_type = re.search('id="ROOM_GHYT">(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('id="ROOM_YCJZMJ">(.*?)<', html, re.S | re.M).group(1)
                house.ho_true_size = re.search('id="ROOM_YCTNMJ">(.*?)<', html, re.S | re.M).group(1)
                house.ho_share_size = re.search('id="ROOM_YCFTMJ">(.*?)<', html, re.S | re.M).group(1)
                house.bu_id = bu_id
                house.co_id = co_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_detail_url), e)

    def get_view_state(self, html):
        tree = etree.HTML(html)
        view_state = tree.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        event_validation = tree.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0]
        data = {
            '__EVENTTARGET': 'PageNavigator1$LnkBtnNext',
            '__EVENTVALIDATION': event_validation,
            '__VIEWSTATE': view_state,
        }
        return data

    def get_all_url_comm(self, data, index, all_comm_url_list):
        response = requests.post(url=url, data=data)
        html = response.text
        comm_url_code_list = re.findall("target=._self. href='.*?code=(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url_code_list
        data = self.get_view_state(html)
        index += 1
        print(index)
        if index == 116:
            return all_comm_url_list
        else:
            return self.get_all_url_comm(data, index, all_comm_url_list)
