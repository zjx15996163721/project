"""
url = http://www.yzfdc.cn/BuildingDish_Project_Search.aspx?Type=1&xmmc=7ACB6A6342A3156FFB95BFA5B078FAF096F20A89668AE5DA
city : 扬州
CO_INDEX : 60
小区数量：807
"""
import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
from retry import retry
import re
import time

url = 'http://www.yzfdc.cn/BuildingDish_Project_Search.aspx?Type=1&xmmc=7ACB6A6342A3156FFB95BFA5B078FAF096F20A89668AE5DA'
co_index = '60'
city = '扬州'

count = 0


class Yangzhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.s = requests.session()

    def start_crawler(self):
        all_comm_url_list = []
        response = self.s.get(url=url)
        html = response.text
        comm_url = re.findall("<td class=.zxlp_01.><a href='(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url
        data = self.get_view_state(html)
        comm_list = self.get_all_url_comm(data, 0, all_comm_url_list)
        self.get_comm_detail(comm_list)

    @retry(tries=3)
    def get_comm_detail(self, comm_list):
        for i in comm_list:
            comm_url = 'http://www.yzfdc.cn/' + i
            try:
                comm = Comm(co_index)
                content = self.s.get(comm_url, headers=self.headers)
                html = content.text
                comm.co_name = re.search('class="zxlp_08".*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_id = re.search('class="zxlp_08" href=.*?ProjectId=(.*?)"', html, re.S | re.M).group(1)
                comm.co_develops = re.search('开 发 商：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_type = re.search('项目类型：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('所属区位：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('建筑面积：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_open_time = re.search('开盘日期：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_handed_time = re.search('交付日期：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('项目具体地址：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.insert_db()
                build_url = re.search('(/BuildingDish_Publicity.aspx\?Projectid=.*?)"', html, re.S | re.M).group(1)
                self.get_build_info(build_url, comm.co_id)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url, co_id):
        bu_url = 'http://www.yzfdc.cn' + build_url
        response = self.s.get(bu_url, headers=self.headers)
        html = response.text
        bu_html = re.search('class="houseNum".*?class="cb', html, re.S | re.M).group()
        bu_url_list = re.findall('href="(.*?)"', bu_html, re.S | re.M)
        for i in bu_url_list:
            try:
                self.get_build_detail(i, co_id)
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, 'http://www.yzfdc.cn/' + i), e)

    def get_build_detail(self, build_url, co_id):
        bu_url = 'http://www.yzfdc.cn/' + build_url
        response = self.s.get(bu_url, headers=self.headers)
        html = response.text
        build = Building(co_index)
        build.bu_num = re.search('查询幢号：.*?<span.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
        bu_html = re.search('<div align="center">已售已备案.*?</table>', html, re.S | re.M).group()
        build_html_list = re.findall('<tr.*?</tr>', bu_html, re.S | re.M)
        all_size = 0
        for i in build_html_list:
            num = re.search('<div.*?<div.*?<div.*?<div.*?<div.*?<div.*?>(.*?)<', i, re.S | re.M).group(1)
            if num:
                all_size += float(num)
        build.bu_build_size = all_size
        build.co_id = co_id
        build.bu_id = re.search('GCZHId=(.*?)$', bu_url).group(1)
        build.insert_db()
        self.get_house_info(co_id, build.bu_id)

    def get_house_info(self, co_id, bu_id):
        house_url = 'http://www.yzfdc.cn/ajax/buildingdishajax.aspx?type=6&xmid=' + co_id + '&gczh=' + bu_id
        response = self.s.get(house_url, headers=self.headers)
        html = response.text
        house_detail_url_list = re.findall("<a href = '(.*?)'", html, re.S | re.M)
        self.get_house_detail(house_detail_url_list, co_id, bu_id)
        house_url_2 = 'http://www.yzfdc.cn/ajax/buildingdishajax.aspx?type=7&xmid=' + co_id + '&gczh=' + bu_id
        response_2 = self.s.get(house_url_2, headers=self.headers)
        html_2 = response_2.text
        house_detail_url_list_2 = re.findall("<a href = '(.*?)'", html_2, re.S | re.M)
        self.get_house_detail(house_detail_url_list_2, co_id, bu_id)

    def get_house_detail(self, house_detail_url_list, co_id, bu_id):
        for i in house_detail_url_list:
            detail_url = 'http://www.yzfdc.cn/' + i
            try:
                house = House(co_index)
                time.sleep(3)
                response = self.s.get(detail_url, headers=self.headers)
                html = response.text
                house.co_name = re.search('lblxmmc.*?>(.*?)<', html, re.S | re.M).group(1)
                house.bu_num = re.search('lbldh.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_name = re.search('lblfh.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('lbljzmj.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_true_size = re.search('lbltnmj.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_share_size = re.search('lblftmj.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_type = re.search('lblfwxz.*?>(.*?)<', html, re.S | re.M).group(1)
                house.ho_room_type = re.search('lblhuxin.*?>(.*?)<', html, re.S | re.M).group(1)
                house.bu_id = bu_id
                house.co_id = co_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, detail_url), e)

    def get_view_state(self, html):
        tree = etree.HTML(html)
        view_state = tree.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        event_validation = tree.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0]
        data = {
            '__EVENTTARGET': 'nav_ProjectList$LnkBtnNext',
            '__EVENTVALIDATION': event_validation,
            '__VIEWSTATE': view_state,
        }
        return data

    def get_all_url_comm(self, data, index, all_comm_url_list):
        response = requests.post(url=url, data=data)
        html = response.text
        comm_url_list = re.findall("<td class=.zxlp_01.><a href='(.*?)'", html, re.S | re.M)
        all_comm_url_list += comm_url_list
        data = self.get_view_state(html)
        index += 1
        print('页码', index)
        if index == 40:
            return all_comm_url_list
        else:
            return self.get_all_url_comm(data, index, all_comm_url_list)
