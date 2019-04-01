"""
url = http://www.ytfcjy.com/public/project/presellCertList.aspx
city : 烟台
CO_INDEX : 58
小区数量：
对应关系：
    小区与楼栋：co_id
    楼栋与房屋：bu_id
"""
import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
import re

url = 'http://www.ytfcjy.com/public/project/presellCertList.aspx'
co_index = '58'
city = '烟台'

count = 0


class Yantai(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        all_comm_url_list = []
        response = requests.get(url=url)
        html = response.text
        comm_url_list = re.findall("target=._self. href='(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url_list
        data = self.get_view_state(html)
        comm_list = self.get_all_url_comm(data, 0, all_comm_url_list)
        self.get_comm_info(comm_list)

    def get_comm_info(self, comm_list):
        for i in comm_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.ytfcjy.com/public/project/' + i
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.findall('PROJECT_XMMC">(.*?)<', html, re.S | re.M)[0]
                comm.co_id = re.findall('ProjectInfo.aspx\?code=(.*?)&', html, re.S | re.M)[0]
                comm.co_address = re.findall('PROJECT_XMDZ">(.*?)<', html, re.S | re.M)[0]
                comm.co_develops = re.findall('PROJECT_KFQY_NAME">(.*?)<', html, re.S | re.M)[0]
                comm.area = re.findall('PROJECT_SZQY">(.*?)<', html, re.S | re.M)[0]
                comm.co_volumetric = re.findall('PROJECT_RJL">(.*?)<', html, re.S | re.M)[0]
                comm.co_build_size = re.findall('PROJECT_GHZJZMJ">(.*?)<', html, re.S | re.M)[0]
                comm.co_pre_sale = re.findall('YSXKZH">(.*?)<', html, re.S | re.M)[0]
                comm.co_all_house = re.findall('YSZTS">(.*?)<', html, re.S | re.M)[0]
                comm.co_plan_pro = re.findall('id="ghxkzInfo" value=".*?,,(.*?)"', html, re.S | re.M)[0]
                comm.co_work_pro = re.findall('id="sgxkzInfo" value=".*?,,(.*?)"', html, re.S | re.M)[0]
                comm.co_land_use = re.findall('id="tdzInfo" value=".*?,,(.*?)"', html, re.S | re.M)[0]
                comm.insert_db()
                global count
                count += 1
                print(count)
                build_url_list = re.findall('id="buildInfo" value="(.*?)"', html, re.S | re.M)
                self.get_build_info(build_url_list, comm.co_id)
            except Exception as e:
                print(e)

    def get_build_info(self, build_url_list, co_id):
        bu_code_list = build_url_list[0].split(';;')
        for i in bu_code_list:
            build = Building(co_index)
            build.co_id = co_id
            code = i.split(',,')
            build.bu_id = code[0]
            build.bu_num = code[1]
            build.insert_db()
            self.get_house_info(build.bu_id)

    def get_house_info(self, bu_id):
        house_url = 'http://www.ytfcjy.com/Common/Agents/ExeFunCommon.aspx'

        payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.Wsba.CBuildTableEx.GetBuildHTMLEx\">\r\n<item>" + \
                  bu_id + "</item>\r\n<item>1</item>\r\n<item>1</item>\r\n<item>80</item>\r\n<item>720</item>\r\n<item>g_oBuildTable</item>\r\n<item> 1=1</item>\r\n</param>\r\n"
        headers = {
            'Content-Type': "text/xml",
        }

        response = requests.request("POST", house_url, data=payload, headers=headers)
        html = response.text
        house_info_list = re.findall("title='(.*?)'", html, re.S | re.M)
        for i in house_info_list:
            house = House(co_index)
            house.ho_name = re.search('房号：(.*?)单元', i, re.S | re.M).group(1)
            house.ho_build_size = re.search('总面积：(.*?) 平方米', i, re.S | re.M).group(1)
            house.ho_type =  re.search('用途：(.*?)户', i, re.S | re.M).group(1)
            house.ho_price =  re.search('价格：(.*?) 元', i, re.S | re.M).group(1)
            house.bu_id = bu_id
            house.info = i
            house.insert_db()

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
        comm_url_list = re.findall("target=._self. href='(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url_list
        data = self.get_view_state(html)
        index += 1
        print(index)
        if index == 38:
            return all_comm_url_list
        else:
            return self.get_all_url_comm(data, index, all_comm_url_list)
