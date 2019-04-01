"""
url = http://www.yanjifc.com/new_house.jsp?mid=1
city : 延吉
CO_INDEX : 147
小区数量：
"""

import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://www.yanjifc.com/new_house.jsp?mid=1'
co_index = '147'
city = '延吉'


class Yanji(object):
    def __init__(self):
        self.headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        page_all_url = 'http://www.yanjifc.com/yanjifc'
        payload = "page=1&rows=10000&module=presell&where="
        response = requests.post(url=page_all_url, data=payload, headers=self.headers)
        html = response.text
        comm_id_list = re.findall('"ID":"(.*?)"', html, re.S | re.M)
        self.get_comm_info(comm_id_list)

    def can_group(self, data):
        try:
            data = data.group(1)
            return data
        except Exception as e:
            return None

    def dict_get(self, dict_data, key):
        try:
            return dict_data[key]
        except Exception as e:
            return None

    def get_comm_info(self, comm_id_list):
        for i in comm_id_list:
            comm = Comm(co_index)
            comm_url = 'http://www.yanjifc.com/yanjifc'
            payload = "id=" + str(i) + "&module=presellById"
            response = requests.post(url=comm_url, data=payload, headers=self.headers)
            html = response.text
            area = re.search('"DISTRICT":"(.*?)"', html, re.S | re.M)
            comm.area = self.can_group(area)
            co_name = re.search('"PROJECTNAME":"(.*?)"', html, re.S | re.M)
            comm.co_name = self.can_group(co_name)
            co_develops = re.search('"ENTERPRISENAME":"(.*?)"', html, re.S | re.M)
            comm.co_develops = self.can_group(co_develops)
            co_pre_sale = re.search('"CERT_NO":"(.*?)"', html, re.S | re.M)
            comm.co_pre_sale = self.can_group(co_pre_sale)
            co_pre_sale_date = re.search('"SIGNDATE":"(.*?)"', html, re.S | re.M)
            comm.co_pre_sale_date = self.can_group(co_pre_sale_date)
            co_type = re.search('"PRESALEUSE":"(.*?)"', html, re.S | re.M)
            comm.co_type = self.can_group(co_type)
            co_land_type = re.search('"USECERTTYPE":"(.*?)"', html, re.S | re.M)
            comm.co_land_type = self.can_group(co_land_type)
            co_land_use = re.search('"LANDUSE":"(.*?)"', html, re.S | re.M)
            comm.co_land_use = self.can_group(co_land_use)
            co_work_pro = re.search('"OPERATIONPERMIT":"(.*?)"', html, re.S | re.M)
            comm.co_work_pro = self.can_group(co_work_pro)
            co_plan_useland = re.search('"PROJECTPERMIT":"(.*?)"', html, re.S | re.M)
            comm.co_plan_useland = self.can_group(co_plan_useland)
            co_address = re.search('"PROJECTLOCATION":"(.*?)"', html, re.S | re.M)
            comm.co_address = self.can_group(co_address)
            comm.co_id = i
            comm.insert_db()
            self.get_build_info(i)

    def get_build_info(self, co_id):
        build_url = 'http://www.yanjifc.com/jdi'
        payload = "activityId=" + str(co_id) + "&module=jtsActBuildingInfo"
        result = requests.post(url=build_url, data=payload, headers=self.headers)
        data = result.json()
        build_list = data['ROWS']['ROW']
        for i in build_list:
            build = Building(co_index)
            build.bu_all_size = self.dict_get(i, 'BUILDING_AREA')
            build.bu_address = self.dict_get(i, 'LOCATION')
            build.bu_num = self.dict_get(i, 'LOCATION')
            build.bu_floor = self.dict_get(i, 'TOTAL_FLOORS')
            build.bu_all_house = self.dict_get(i, 'TOTAL_SET')
            build.co_build_structural = self.dict_get(i, 'STRUCTURE')
            build.bu_id = self.dict_get(i, 'RESOURCE_GUID')
            build.co_id = co_id
            build.insert_db()
            self.get_house_info(co_id, build.bu_id)

    def get_house_info(self, co_id, bu_id):
        house_url = 'http://www.yanjifc.com/jdi'
        payload = "page=1&rows=10000&module=jtsActHouses&buildingGuid=" + bu_id + "&activityId=" + co_id
        response = requests.post(house_url, data=payload, headers=self.headers)
        html = response.json()
        house_list = html['ROWS']['ROW']
        for i in house_list:
            house = House(co_index)
            house.ho_build_size = self.dict_get(i, 'BUILDING_AREA')
            house.ho_floor = self.dict_get(i, 'UNIT')
            house.ho_type = self.dict_get(i, 'PLANNING_USAGE')
            house.ho_true_size = self.dict_get(i, 'INNER_AREA')
            house.co_build_structural = self.dict_get(i, 'STRUCTURE')
            house.ho_name = self.dict_get(i, 'PART')
            house.bu_id = bu_id
            house.co_id = co_id
            house.insert_db()
