"""
url = http://house.bffdc.gov.cn/public/project/presellCertList2.aspx
city : 平顶山
CO_INDEX : 36
小区数量：
对应关系：小区对楼栋：co_name
        楼栋对房屋：bu_num
"""

import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
import re

url = 'http://house.bffdc.gov.cn/public/project/presellCertList2.aspx'
co_index = '36'
city = '平顶山'
count = 0


class Pingdingshan(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        all_comm_url_list = []
        response = requests.get(url=url, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        comm_url = tree.xpath('//tr[@class="TR_BG_list"]/td/a/@href')
        all_comm_url_list += comm_url
        data = self.get_view_state(html)
        comm_list = self.get_all_url_comm(data, 0, all_comm_url_list)
        self.get_comm_detail(comm_list)

    def get_comm_detail(self, comm_list):
        for i in comm_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://house.bffdc.gov.cn/public/project/' + i
                response = requests.get(comm_url)
                html = response.text
                comm.co_name = re.search('PROJECT_XMMC">(.*?)<', html, re.S | re.M).group(1)
                comm.co_develops = re.search('PROJECT_KFQY_NAME">(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('PROJECT_XMDZ">(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('PROJECT_SZQY">(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale = re.search('YSXKZH">(.*?)<', html, re.S | re.M).group(1)
                comm.insert_db()
                build_info = re.search('id="buildInfo".*?value="(.*?)"', html, re.S | re.M).group(1)
                build_url_list = build_info.split(';;')
                self.get_build_info(build_url_list, comm.co_name)
                global count
                count += 1
                print(count)
            except Exception as e:
                print(e)

    def get_build_info(self, build_url_list, co_name):
        for i in build_url_list:
            try:
                build = Building(co_index)
                code = i.split(',,')
                build.bu_num = code[1]
                build.co_name = co_name
                build.insert_db()
                self.get_house_info(code, co_name)
            except Exception as e:
                print(e)

    def get_house_info(self, code, co_name):
        house_url = 'http://house.bffdc.gov.cn/Common/Agents/ExeFunCommon.aspx?'
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.Wsba.CBuildTableEx.GetBuildHTMLEx\">\r\n<item>" + \
                  code[
                      0] + "</item>\r\n<item>1</item>\r\n<item>1</item>\r\n<item>55</item>\r\n<item>840</item>\r\n<item>g_oBuildTable</item>\r\n<item>false</item>\r\n<item> 1=1</item>\r\n</param>\r\n"
        headers = {
            'Content-Type': "text/xml",
        }
        response = requests.post(url=house_url, data=payload, headers=headers)
        html = response.text
        info = re.findall("title='(.*?)'", html, re.S | re.M)
        for i in info:
            try:
                house = House(co_index)
                house.bu_num = code[1]
                house.ho_name = re.search('房号：(.*?)\r\n', i).group(1)
                house.ho_type = re.search('用途：(.*?)\r\n', i).group(1)
                house.ho_room_type = re.search('户型：(.*?)\r\n', i).group(1)
                house.ho_build_size = re.search('总面积：(.*?)\r\n', i).group(1)
                house.co_name = co_name
                house.insert_db()
            except Exception as e:
                print(e)

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
        tree = etree.HTML(html)
        comm_url_list = tree.xpath('//tr[@class="TR_BG_list"]/td/a/@href')
        all_comm_url_list += comm_url_list
        data = self.get_view_state(html)
        index += 1
        print(index)
        if index == 15:
            return all_comm_url_list
        else:
            return self.get_all_url_comm(data, index, all_comm_url_list)
