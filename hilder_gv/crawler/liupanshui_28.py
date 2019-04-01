"""
url = http://www.lpsfdc.cn/Templets/LPS/aspx/ProjectList.aspx
city : 六盘水
CO_INDEX : 28
小区数量：807
"""
import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
from retry import retry
import re

url = 'http://www.lpsfdc.cn/Templets/LPS/aspx/ProjectList.aspx'
co_index = '28'
city = '六盘水'

count = 0


class Liupanshui(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        all_comm_url_list = []
        response = requests.get(url=url)
        html = response.text
        tree = etree.HTML(html)
        comm_url = tree.xpath('//a[@target="_self"]/@href')
        all_comm_url_list += comm_url
        data = self.get_view_state(html)
        comm_list = self.get_all_url_comm(data, 0, all_comm_url_list)
        self.get_comm_detail(comm_list)

    @retry(tries=3)
    def get_comm_detail(self, comm_list):
        for i in comm_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.lpsfdc.cn/Templets/LPS/aspx/' + i
                content = requests.get(comm_url)
                html = content.text
                co_name_list = re.findall('项目名称：.*?>(.*?)<', html, re.S | re.M)
                co_id_list = re.findall('hdProjectCode" value="(.*?)"', html, re.S | re.M)
                co_develops_list = re.findall('开发企业：.*?>(.*?)<', html, re.S | re.M)
                co_build_size_list = re.findall('TJ_ZMJ">(.*?)<', html, re.S | re.M)
                co_address_list = re.findall('Pro_XMDZ">(.*?)<', html, re.S | re.M)
                co_owner_list = re.findall('Pro_ZZZSBH">(.*?)<', html, re.S | re.M)
                co_pre_sale_list = re.findall('Pro_XKZH">(.*?)<', html, re.S | re.M)
                co_all_house_list = re.findall('TJ_HZYSTS">(.*?)<', html, re.S | re.M)
                for i in range(0, len(co_name_list)):
                    try:
                        comm.co_name = co_name_list[i]
                        comm.co_id = co_id_list[i]
                        comm.co_develops = co_develops_list[i]
                        comm.co_build_size = co_build_size_list[i]
                        comm.co_address = co_address_list[i]
                        comm.co_owner = co_owner_list[i]
                        comm.co_pre_sale = co_pre_sale_list[i]
                        comm.co_all_house = co_all_house_list[i]
                        comm.insert_db()
                        # global count
                        # count += 1
                        # print(count)
                    except Exception as e:
                        print('co_index={}, commiunty error'.format(co_index,), e)
                    build_url_list = re.findall("radiobuild' id='build(.*?)'", html, re.S | re.M)
                    build_name_list = re.findall("radiobuild.*?<span.*?>(.*?)<", html, re.S | re.M)
                    for i in range(0, len(build_url_list)):
                        build = Building(co_index)
                        build.bu_id = build_url_list[i]
                        build.bu_num = build_name_list[i]
                        build.co_id = co_id_list[0]
                        build.insert_db()
                    self.get_build_info(build_url_list)
            except Exception as e:
                print(e)

    @retry(tries=3)
    def get_build_info(self, build_url):
        for bu_id in build_url:
            try:
                bu_url = "http://www.lpsfdc.cn/Common/Agents/ExeFunCommon.aspx"
                payload = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\r\n<param funname=\"SouthDigital.CMS.CBuildTableEx.GetPublicHTML\">\r\n<item>" + bu_id + "</item>\r\n<item> 1=1</item>\r\n</param>"
                headers = {'Content-Type': "application/xml"}
                response = requests.request("POST", bu_url, data=payload, headers=headers)
                html = response.text
                house_url_list = re.findall('<div class="lfzt"><a href="(.*?)".*?</a></div>', html, re.S | re.M)
                self.get_house_info(house_url_list, bu_id)
            except Exception as e:
                print(e)

    @retry(tries=3)
    def get_house_info(self, house_url_list, bu_id):
        for i in house_url_list:
            try:
                house = House(co_index)
                house_url = 'http://www.lpsfdc.cn/Templets/LPS/aspx/' + i
                response = requests.get(house_url)
                html = response.text
                ho_name = re.findall('ROOM_ROOMNO">(.*?)<', html, re.S | re.M)[0]
                ho_type = re.findall('ROOM_FWLX">(.*?)<', html, re.S | re.M)[0]
                ho_build_size = re.findall('ROOM_YCJZMJ">(.*?)<', html, re.S | re.M)[0]
                ho_true_size = re.findall('ROOM_YCTNMJ">(.*?)<', html, re.S | re.M)[0]
                ho_share_size = re.findall('ROOM_YCFTMJ">(.*?)<', html, re.S | re.M)[0]
                house.ho_name = ho_name
                house.ho_type = ho_type
                house.ho_build_size = ho_build_size
                house.ho_true_size = ho_true_size
                house.ho_share_size = ho_share_size
                house.bu_id = bu_id
                house.insert_db()
            except Exception as e:
                print(e)

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
        tree = etree.HTML(html)
        comm_url_list = tree.xpath('//a[@target="_self"]/@href')
        all_comm_url_list += comm_url_list
        data = self.get_view_state(html)
        index += 1
        print('页码', index)
        if index == 53:
            return all_comm_url_list
        else:
            return self.get_all_url_comm(data, index, all_comm_url_list)
