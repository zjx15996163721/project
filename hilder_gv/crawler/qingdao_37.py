"""
url = https://www.qdfd.com.cn/qdweb/realweb/fh/FhProjectQueryNew.jsp?page=1&rows=100000
city : 青岛
CO_INDEX : 37
小区数量：
对应关系：小区对楼栋：co_id
        楼栋对房屋：bu_id
"""
import requests
from backup.comm_info import Comm, Building, House
import re

url = 'https://www.qdfd.com.cn/qdweb/realweb/fh/FhProjectQueryNew.jsp?page=1&rows=100000'
co_index = '37'
city = '青岛'


class Qingdao(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url=url, headers=self.headers)
        html = response.text
        comm_url_list = re.findall('javascript:detailProjectInfo\("(.*?)"\)', html, re.S | re.M)
        self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'https://www.qdfd.com.cn/qdweb/realweb/fh/FhProjectInfo.jsp'
                data = {'projectID': i}
                response = requests.post(url=comm_url, data=data, headers=self.headers)
                html = response.text
                comm.co_id = i
                comm.co_name = re.findall('bszn_title">(.*?)<', html, re.S | re.M)[0].strip()
                comm.area = re.findall('所在区县：.*?<span>(.*?)<', html, re.S | re.M)[0].strip()
                comm.co_address = re.findall('项目地址：.*?<span>(.*?)<', html, re.S | re.M)[0].strip()
                comm.co_develops = re.findall('企业名称：.*?<a.*?>(.*?)<', html, re.S | re.M)[0].strip()
                comm.co_all_house = re.findall('<td>总套数.*?<td class="xxxx_list3">(.*?)<', html, re.S | re.M)[0].strip()
                comm.co_build_size = re.findall('<td>总面积.*?<td class="xxxx_list3">(.*?)<', html, re.S | re.M)[0].strip()
                comm.insert_db()
                build_logo_list = re.findall('javascript:getBuilingList\("(.*?)"', html, re.S | re.M)
                self.get_build_info(build_logo_list, i)
            except Exception as e:
                print('青岛小区问题,url post data is:={}'.format(data), e)

    def get_build_info(self, build_logo_list, preid):
        for build_logo in build_logo_list:
            try:
                build_url = 'https://www.qdfd.com.cn/qdweb/realweb/fh/FhBuildingList.jsp?preid=' + build_logo
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                bu_num_list = re.findall('javascript:showHouseStatus.*?>(.*?)</a', html, re.S | re.M)
                bu_all_house_list = re.findall(
                    'javascript:showHouseStatus.*?center.*?center.*?center.*?center.*?center.*?>(.*?)<', html,
                    re.S | re.M)
                house_code_list = re.findall("javascript:showHouseStatus\((.*?)\)'>", html, re.S | re.M)
                for i in range(len(bu_num_list)):
                    try:
                        build = Building(co_index)
                        bu_code_list = re.findall('"(.*?)"', house_code_list[i])
                        build.bu_num = bu_num_list[i]
                        build.bu_all_house = bu_all_house_list[i]
                        build.co_id = preid
                        build.bu_id = bu_code_list[0]
                        build.insert_db()
                        co_id = bu_code_list[2]
                        house_id = bu_code_list[1]
                        self.get_house_info(build.bu_id, co_id, house_id)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print('青岛楼栋问题,url:={}'.format(build_url), e)

    def get_house_info(self, bu_id, co_id, house_id):
        house_url = 'https://www.qdfd.com.cn/qdweb/realweb/fh/FhHouseStatus.jsp?buildingID=' + bu_id + '&startID=' + house_id + '&projectID=' + co_id
        response = requests.get(house_url, headers=self.headers)
        html = response.text
        ho_name_list = re.findall('javascript:houseDetail.*?>(.*?)<', html, re.S | re.M)
        for i in ho_name_list:
            try:
                house = House(co_index)
                house.bu_id = bu_id
                house.ho_name = i
                house.insert_db()
            except Exception as e:
                print('青岛房号问题,url:={}'.format(house_url), e)
