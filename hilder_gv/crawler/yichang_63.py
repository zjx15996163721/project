"""
url = http://www.ycfcjy.com
city :  宜昌
CO_INDEX : 63
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Building, House
import requests
import json

co_index = 63


class Yichang(Crawler):
    def __init__(self):
        self.start_url = "http://www.ycfcjy.com"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def start_crawler(self):
        url = self.start_url + "/api/buildInfos/pageHousePreSales?page=1&limit=10000&state=2&code=1"
        res = requests.get(url, headers=self.headers)
        dict = json.loads(res.text)
        data = dict["data"]["data"]

        count = 0

        for i in data:
            try:
                id = i["blockNumber"]
                self.comm(id)
                count = count + 1
                print(count)
            except Exception as e:
                print(e)

    def comm(self, id):
        bu = Building(co_index)

        house_url = self.start_url + "/api/buildInfos/getHouseInfosByPannelNumber?pannelNumber=" + str(id)
        comm_url = self.start_url + "/api/buildInfos/getHomePageBuildingInfo?blockNumber=" + str(id)
        comm_detail_url = self.start_url + "/api/buildInfos/getDetailsBuildingInfo?blockNumber=" + str(id)

        comm_res = requests.get(comm_url)
        comm_detail_res = requests.get(comm_detail_url)
        house_res = requests.get(house_url)
        comm_dict = json.loads(comm_res.text)
        comm_detail_dict = json.loads(comm_detail_res.text)
        house_dict = json.loads(house_res.text)

        bu.bu_id = id
        bu.bu_num = comm_dict["data"]["nameBuildings"]
        bu.area = comm_detail_dict['data']['houseingArea']
        bu.bu_address = comm_dict["data"]["houseaddress"]
        bu.bu_pre_sale = comm_detail_dict["data"]["yszh"]
        bu.bu_type = comm_dict["data"]["propertycategory"]
        bu.bo_develops = comm_dict["data"]["companyName"]

        bu.insert_db()

        house_num = house_dict["data"]
        for hu in house_num:
            ho = House(co_index)
            h = hu["data"]
            if len(h) > 0:
                for i in h:
                    try:
                        room_id = i["houseNumber"]
                        room_url = self.start_url + "/api/buildInfos/getHouseInfoByHouseNumber?houseNumber=" + str(
                            room_id)
                        res = requests.get(room_url, headers=self.headers)
                        dict = json.loads(res.text)
                        ho.bu_id = id
                        # ho.ho_num = room_id
                        ho.ho_name = dict["data"]["houseNo"]
                        ho.ho_build_size = dict["data"]["buildArea"]
                        ho.ho_true_size = dict["data"]["jacketArea"]
                        ho.ho_share_size = dict["data"]["apportionedArea"]
                        ho.ho_floor = dict["data"]["nominalLevel"]
                        ho.insert_db()
                    except Exception as e:
                        print(e)
            else:
                continue
