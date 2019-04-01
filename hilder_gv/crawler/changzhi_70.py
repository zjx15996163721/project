"""
url = http://www.sxczfdc.com/pubinfo/More_xm.aspx
city : 长治
CO_INDEX : 70
小区数量：
对应关系：
    小区与楼栋：
    楼栋与房屋：
"""
import requests
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re

url = 'http://www.sxczfdc.com/pubinfo/More_xm.aspx'
co_index = '70'
city = '长治'


class Changzhi(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='下一页.*?page=(.*?)"',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_page_url = 'http://www.sxczfdc.com/pubinfo/More_xm.aspx?page=' + str(i)
            response = requests.get(all_page_url, headers=self.headers)
            html = response.text
            comm_url_list = re.findall('style="background-color: .*?(Pub_lpxx.aspx\?DevProjectId=.*?)"', html,
                                       re.S | re.M)
            area_list = re.findall('style="background-color: .*?center">(.*?)<', html, re.S | re.M)
            self.get_comm_info(comm_url_list, area_list)

    def get_comm_info(self, comm_url_list, area_list):
        for i in range(len(comm_url_list)):
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.sxczfdc.com/pubinfo/' + comm_url_list[i]
                comm.area = area_list[i]
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_name = re.findall('ProjectInfo1_lblProjectName">(.*?)<', html, re.S | re.M)[0]
                comm.co_address = re.findall('ProjectInfo1_lblProjectAddress">(.*?)<', html, re.S | re.M)[0]
                comm.co_develops = re.findall('ProjectInfo1_lblCorpName">(.*?)<', html, re.S | re.M)[0]
                comm.co_type = re.findall('ProjectInfo1_lblProjectType">(.*?)<', html, re.S | re.M)[0]
                comm.co_build_start_time = re.findall('ProjectInfo1_lblJhkgrq">(.*?)<', html, re.S | re.M)[0]
                comm.ProjectInfo1_lblJhjfsyrq = re.findall('ProjectInfo1_lblJhjfsyrq">(.*?)<', html, re.S | re.M)[0]
                comm.co_size = re.findall('ProjectInfo1_lblXmzgm">(.*?)<', html, re.S | re.M)[0]
                comm.co_build_size = re.findall('ProjectInfo1_lblZjzmj">(.*?)<', html, re.S | re.M)[0]
                comm.co_green = re.findall('ProjectInfo1_lblJdl">(.*?)<', html, re.S | re.M)[0]
                comm.co_volumetric = re.findall('ProjectInfo1_lblRjl">(.*?)<', html, re.S | re.M)[0]
                comm.insert_db()
                build_url_list = re.findall('(Pub_ysxx.aspx\?PresellId=.*?)"', html, re.S | re.M)
                self.get_build_info(build_url_list, comm.co_name)
            except Exception as e:
                print(e)

    def get_build_info(self, build_url_list, co_name):
        for i in build_url_list:
            try:
                build = Building(co_index)
                build.co_name = co_name
                build_url = 'http://www.sxczfdc.com/pubinfo/' + i
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                # build_detail_url = re.findall('(Pub_dtxx.aspx\?ProjectBuildingID=.*?)"', html, re.S | re.M)[0]
                for k in re.findall('(Pub_dtxx.aspx\?ProjectBuildingID=.*?)"', html, re.S | re.M):
                    try:
                        build_url_detail = 'http://www.sxczfdc.com/pubinfo/' + k
                        result = requests.get(build_url_detail, headers=self.headers)
                        content = result.text
                        build.bu_num = re.findall('BuildingInfo1_lblBuildingName">(.*?)<', content, re.S | re.M)[0]
                        build.bu_all_house = re.findall('BuildingInfo1_lblZts">(.*?)<', content, re.S | re.M)[0]
                        build.bu_floor = re.findall('BuildingInfo1_lblZcs">(.*?)<', content, re.S | re.M)[0]
                        build.bu_build_size = re.findall('BuildingInfo1_lblJzmj">(.*?)<', content, re.S | re.M)[0]
                        build.bu_live_size = re.findall('BuildingInfo1_lblZzmj">(.*?)<', content, re.S | re.M)[0]
                        build.bu_pre_sale = re.findall('BuildingInfo1_lblYsxkzh">(.*?)<', content, re.S | re.M)[0]
                        build.bu_pre_sale_date = re.findall('BuildingInfo1_lblYsxkzfzrq">(.*?)<', content, re.S | re.M)[0]
                        build.insert_db()
                        house_url_list = re.findall("onClick=.getMoreHouseInfo\('(.*?)'\)", content, re.S | re.M)
                        self.get_house_info(house_url_list, co_name, build.bu_num)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

    def get_house_info(self, house_url_list, co_name, bu_num):
        for i in house_url_list:
            try:
                house = House(co_index)
                house.co_name = co_name
                house.bu_num = bu_num
                house_url = 'http://www.sxczfdc.com/pubinfo/' + i
                response = requests.get(house_url, headers=self.headers)
                html = response.text
                house.ho_floor = re.findall('HouseInfo1_lblFwlc">(.*?)<', html, re.S | re.M)[0]
                house.ho_name = re.findall('HouseInfo1_lblFwfh">(.*?)<', html, re.S | re.M)[0]
                house.ho_type = re.findall('HouseInfo1_lblFwlx">(.*?)<', html, re.S | re.M)[0]
                house.ho_room_type = re.findall('HouseInfo1_lblFwhx">(.*?)<', html, re.S | re.M)[0]
                house.ho_build_size = re.findall('HouseInfo1_lblycfwjzmj">(.*?)<', html, re.S | re.M)[0]
                house.ho_true_size = re.findall('HouseInfo1_lblycfwtnmj">(.*?)<', html, re.S | re.M)[0]
                house.ho_share_size = re.findall('HouseInfo1_lblycfwftmj">(.*?)<', html, re.S | re.M)[0]
                house.orientation = re.findall('HouseInfo1_lblCx">(.*?)<', html, re.S | re.M)[0]
                house.insert_db()
            except Exception as e:
                print(e)
