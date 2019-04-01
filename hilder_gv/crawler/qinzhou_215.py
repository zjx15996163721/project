"""
url = "http://202.103.219.149:7000/ajax/LeadingMIS.CommonModel.CommonQuery.WebUI.AjaxManage.QueryDataParser,LeadingMIS.CommonModel.CommonQuery.WebUI.ashx"
city: 钦州
CO_INDEX: 215
小区数量：
对应关系：
"""

import requests
from backup.comm_info import Comm, Building, House
import re

url = "http://202.103.219.149:7000/ajax/LeadingMIS.CommonModel.CommonQuery.WebUI.AjaxManage.QueryDataParser,LeadingMIS.CommonModel.CommonQuery.WebUI.ashx"
co_index = '215'
city = '钦州'
count = 0


class Qinzhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        querystring = {"_method": "GetDataToDynamicInXml", "_session": "rw"}
        payload = "xmlInfo=%263Croot%2620QueryCode%263D%2622ProjectIntroduce%2622%2620PageIndex%263D%26221%2622%2620PageSize%263D%262215%2622%2620SortField%263D%2622%2620ORDER%2620BY%2620Name%2622%2620QueryString%263D%2622QueryCode%263DProjectIntroduce%2626amp%263BShowModeCode%263Ddefault%2622%2620BeginDate%263D%2622%262000%263A00%263A00%2622%2620EndDate%263D%2622%262023%263A59%263A59%2622%2620Flag%263D%2622TitleBody%2622%2620TitlesWidthInfo%263D%2622EnterPriseName%267C0%2624Name%267C0%2624Location%267C0%2624SoilUse%267C0%2622%2620IsUseOCache%263D%26220%2622%2620IsUserID%263D%26220%2622%2620SiteId%263D%26228907bd13-1d14-4f9e-8c01-e482d9590d10%2622%2620LockedColumn%263D%26220%2622%2620IsLocked%263D%26220%2622%2620ClientWidth%263D%26221601%2622%2620ShowModeCode%263D%2622default%2622%2620Language%263D%2622chinese%2622/%263E"
        response = requests.request("POST", url, data=payload, params=querystring)
        html = response.text
        comm_info_list = re.findall('class="tdctfield tdctwidthset ".*?</tr>', html, re.S | re.M)
        for i in comm_info_list:
            comm = Comm(co_index)
            comm.co_develops = re.search('class="spanctfield".*?>(.*?)<', i, re.S | re.M).group(1)
            comm.co_name = re.search('class="spanctfield".*?class="spanctfield".*?<a.*?>(.*?)<', i, re.S | re.M).group(
                1)
            comm.co_address = re.search('class="spanctfield".*?class="spanctfield".*?class="spanctfield".*?>(.*?)<', i,
                                        re.S | re.M).group(1)
            comm.co_type = re.search(
                'class="spanctfield".*?class="spanctfield".*?class="spanctfield".*?class="spanctfield".*?>(.*?)<', i,
                re.S | re.M).group(1)
            comm.co_id = re.search('EnterPriseName_(.*?)"', i, re.S | re.M).group(1)
            comm.insert_db()
            self.get_build_info(comm.co_id)

    def get_build_info(self, co_id):
        build_url = "http://202.103.219.149:7000/ajax/LeadingMIS.CommonModel.CommonQuery.WebUI.AjaxManage.QueryDataParser,LeadingMIS.CommonModel.CommonQuery.WebUI.ashx"
        querystring = {"_method": "GetDataToDynamicInXml", "_session": "rw"}
        payload = "xmlInfo=%263Croot%2620QueryCode%263D%2622BuildingsInfo%2622%2620PageIndex%263D%26221%2622%2620PageSize%263D%262215%2622%2620SortField%263D%2622%2620ORDER%2620BY%2620Name%2622%2620QueryString%263D%2622QueryCode%263DBuildingsInfo%2626amp%263BProjectID%263D" + co_id + "%2622%2620BeginDate%263D%2622%262000%263A00%263A00%2622%2620EndDate%263D%2622%262023%263A59%263A59%2622%2620Flag%263D%2622TitleBody%2622%2620TitlesWidthInfo%263D%2622BuildNo%267C0%2624Name%267C0%2624FloorCount%267C0%2624RoomCount%267C0%2624YCJZArea%267C0%2624Structure%267C0%2624YSXKCer%267C0%2624ZJJG%267C0%2622%2620IsUseOCache%263D%26220%2622%2620IsUserID%263D%26220%2622%2620SiteId%263D%26228907bd13-1d14-4f9e-8c01-e482d9590d10%2622%2620LockedColumn%263D%26220%2622%2620IsLocked%263D%26220%2622%2620ClientWidth%263D%26221601%2622%2620ShowModeCode%263D%2622default%2622%2620Language%263D%2622chinese%2622/%263E"
        try:
            response = requests.request("POST", build_url, data=payload, params=querystring)
            html = response.text
            build_info_list = re.findall('<tr.*?>.*?</tr>', html, re.S | re.M)[1:]
            for i in build_info_list:
                build = Building(co_index)
                build.co_id = co_id
                build.bu_num = re.search('<span class="spanctfield".*?<span class="spanctfield".*?>.*?<a.*?>(.*?)<', i,
                                         re.S | re.M).group(1)
                build.bu_floor = re.search(
                    '<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?>(.*?)<', i,
                    re.S | re.M).group(1)
                build.bu_pre_sale = re.search(
                    '<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?<span class="spanctfield".*?>(.*?)<',
                    i, re.S | re.M).group(1)
                build.bu_id = re.search('id="Tr_(.*?)"', i, re.S | re.M).group(1)
                build.insert_db()
                self.get_house_info(co_id, build.bu_id)
        except Exception as e:
            print('请求错误，url={},data={},params={}'.format(build_url, payload, querystring))

    def get_house_info(self, co_id, bu_id):
        house_url = "http://202.103.219.149:7000/LeadingEstate/buildingtable/ShowNewBuildingTable.aspx"
        payload = "IsShowHouse=1&BuidID=" + bu_id
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        try:
            response = requests.request("POST", house_url, data=payload, headers=headers)
            html = response.text
            house_info_list = re.findall('HouseID.*?\}', html, re.S | re.M)
            for i in house_info_list:
                house = House(co_index)
                house.bu_id = bu_id
                house.co_id = co_id
                house.ho_name = re.search('"YCHouseNo":"(.*?)"', i, re.S | re.M).group(1)
                house.ho_floor = re.search('"ActFLoor":"(.*?)"', i, re.S | re.M).group(1)
                house.ho_build_size = re.search('"YCJZArea":"(.*?)"', i, re.S | re.M).group(1)
                house.ho_true_size = re.search('"YCTNJZArea":"(.*?)"', i, re.S | re.M).group(1)
                house.ho_share_size = re.search('"YCFTJZArea":"(.*?)"', i, re.S | re.M).group(1)
                house.insert_db()
        except Exception as e:
            print('请求错误，url={},data={}'.format(house_url, payload))