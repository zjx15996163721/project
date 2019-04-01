"""
url = http://www.hbczfdc.com:4993/HPMS/ProjectInfoList.aspx
city : 沧州
CO_INDEX : 103
小区数量：
"""

import requests
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re
from lxml import etree

url = 'http://www.hbczfdc.com:4993/HPMS/ProjectInfoList.aspx'
co_index = '103'
city = '沧州'


class Cangzhou(object):
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
                       page_count_rule='PageNavigator1_LblPageCount">(.*?)<',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            data = {
                '__EVENTTARGET': 'PageNavigator1$LnkBtnGoto',
                '__VIEWSTATE': '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',
                '__EVENTVALIDATION': 'LxxNpsWs7rQxyKjUMRIEmE15Tgh2GIYPnRuyWK6QLBfr0LjBkUgIzrz2OdCOoYvM3j1PJgXlbk47HQPIZYhE8O31PPmWgatzJzZCY53FR/uvWPIs73jw8AdKWznSEP4QefnP3TemxtamTpIi1nkG5UtnK1EkhLhtvq3+MEvdEr9nuTV2LfhoH3uJTzT2kJLuxoZ/WzuAlxYlksr8R+PakaKMafw+zH9LBFOzXWvrZLeXR3YaVMTfILOKXFJepQO1dYIYGY6P3AGEzDxIY1sYMUhA7KfBzUBntpwpOfUwomyEI+40F6QOJlEFjd4mwbzYgCdvieTMBaXnsxOi2vLHPC983sJdR0Ljn6XOEhXPDDXEetVJ7l3NndMBBM287GbwcKZCH1CXJZZPXSQ3',
                'PageNavigator1$txtNewPageIndex': int(i),
            }
            response = requests.post(url, data=data, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            comm_url_list = tree.xpath('//*[@id="wrapper"]/div[3]/div[1]/div[2]/table/tr/td[2]/a/@href')
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm_url = 'http://www.hbczfdc.com:4993/' + i.replace('../', '')
            try:
                comm = Comm(co_index)
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.search('id="Project_XMMC">(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('id="Project_XMDZ">(.*?)<', html, re.S | re.M).group(1)
                comm.co_develops = re.search('id="Project_COMPANYNAME">(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('id="Project_AREA_NAME">(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('id="Project_GHZJZMJ">(.*?)<', html, re.S | re.M).group(1)
                comm.co_volumetric = re.search('id="Project_RJL">(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale = re.search('id="presellInfo".*?,,(.*?)"', html, re.S | re.M).group(1)
                comm.co_land_use = re.search('id="tdzInfo".*?,,(.*?)"', html, re.S | re.M).group(1)
                comm.co_work_pro = re.search('id="sgxkzInfo".*?,,(.*?)"', html, re.S | re.M).group(1)
                comm.co_plan_pro = re.search('id="ghxkzInfo".*?,,(.*?)"', html, re.S | re.M).group(1)
                comm.co_id = re.search('code=(.*?)$', comm_url, re.S | re.M).group(1)
                comm.insert_db()
                build = Building(co_index)
                build.bu_id = re.search("name='radiobuild'.*? bid=(.*?) ", html, re.S | re.M).group(1)
                build.bu_num = re.search("name='radiobuild'.*?<span.*?>(.*?)<", html, re.S | re.M).group(1)
                build.co_id = comm.co_id
                build.insert_db()
                self.get_build_info(build.bu_id, comm.co_id)
            except Exception as e:
                print('小区页面错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, bu_id, co_id):
        build_url = "http://www.hbczfdc.com:4993/Common/Agents/ExeFunCommon.aspx"
        querystring = {"0.09441095562074753": "", "req": "1524625947272"}
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.Wsba2.CBuildTableV2.GetBuildHTMLEx\">\r\n<item>../</item>\r\n<item>" + bu_id + "</item>\r\n<item>1</item>\r\n<item>1</item>\r\n<item>80</item>\r\n<item>840</item>\r\n<item>g_oBuildTable</item>\r\n<item> 1=1</item>\r\n<item>1</item>\r\n<item></item>\r\n<item></item>\r\n</param>\r\n"
        headers = {'Content-Type': "text/html"}
        response = requests.post(build_url, data=payload, headers=headers, params=querystring)
        html = response.text
        house_id_list = re.findall("clickRoom\('(.*?)'\)", html, re.S | re.M)
        self.get_house_info(house_id_list, bu_id, co_id)

    def get_house_info(self, house_id_list, bu_id, co_id):
        for i in house_id_list:
            house_url = 'http://www.hbczfdc.com:4993/HPMS/RoomInfo.aspx?code=' + i
            try:
                house = House(co_index)
                response = requests.get(house_url, headers=self.headers)
                html = response.text
                house.bu_id = bu_id
                house.co_id = co_id
                house.ho_name = re.search('id="ROOM_HH">(.*?)<', html, re.S | re.M).group(1)
                house.ho_floor = re.search('id="ROOM_MYC">(.*?)<', html, re.S | re.M).group(1)
                house.ho_type = re.search('id="ROOM_FWYT">(.*?)<', html, re.S | re.M).group(1)
                house.ho_room_type = re.search('id="ROOM_HX">(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('id="ROOM_YCJZMJ">(.*?)<', html, re.S | re.M).group(1)
                house.ho_true_size = re.search('id="ROOM_YCTNJZMJ">(.*?)<', html, re.S | re.M).group(1)
                house.ho_share_size = re.search('id="ROOM_YCFTJZMJ">(.*?)<', html, re.S | re.M).group(1)
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_url), e)
