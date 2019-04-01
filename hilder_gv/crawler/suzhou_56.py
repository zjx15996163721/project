"""
url = http://zjjg.0557fdc.com:9555/Default.aspx
city : 宿州
CO_INDEX : 56
小区数量：
对应关系：
    小区与楼栋：co_id
    楼栋与房屋：bu_num
"""
import requests
from backup.comm_info import Comm, Building, House
from backup.producer import ProducerListUrl
import re

url = 'http://zjjg.0557fdc.com:9555/Default.aspx'
co_index = '56'
city = '宿州'


class Suzhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        html = response.text
        comm_url_list = re.findall('<a id=".*?href="(.*?)"', html, re.S | re.M)
        self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://zjjg.0557fdc.com:9555/' + i
                comm.co_name = '小区名称：.*?<td.*?>(.*?)<'
                comm.area = '所属区域：.*?<td.*?>(.*?)<'
                comm.co_address = '座落：.*?<td.*?>(.*?)<'
                comm.co_develops = '开发商名称：.*?<td.*?>(.*?)<'
                comm.co_pre_sale = '开发企业营业执照号.*?<td.*?>(.*?)<'
                comm.co_all_house = 'Label1">(.*?)<'
                comm.co_build_size = 'Label2">(.*?)<'
                comm.co_id = 'action=.*?xqbm=(.*?)"'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=comm.to_dict(),
                                    current_url_rule='action="(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                build_url_list = p.get_details()
                self.get_build_info(build_url_list)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url_list):
        for i in build_url_list:
            try:
                build = Building(co_index)
                build_code = re.search('xqbm=(.*?)$', i).group(1)
                build_url = 'http://zjjg.0557fdc.com:9555/xiaoqu/donginfo.aspx?xqbm=' + build_code
                build.bu_num = 'Labeldongmc">(.*?)<'
                build.bu_pre_sale = 'Labelyszheng">(.*?)<'
                build.bu_floor = 'Labelsceng">(.*?)<'
                build.bu_address = 'Label1zuoluo">(.*?)<'
                build.bo_build_start_time = 'Label1kaigong">(.*?)<'
                build.co_build_structural = 'Labeljiegou">(.*?)<'
                build.co_id = 'donginfo.aspx\?xqbm=(.*?)"'
                build.bu_id = 'id="DropDownList1".*?value="(.*?)"'
                p = ProducerListUrl(page_url=build_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=build.to_dict(),
                                    current_url_rule='location\.href=(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                house_url_list = p.get_details()
                self.get_house_info(house_url_list)
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_info(self, house_url_list):
        for i in house_url_list:
            try:
                dongid = re.search('dongid=(.*?)&', i).group(1)
                roomid = re.search('roomid=(.*?)&', i).group(1)
                house_url = 'http://zjjg.0557fdc.com:9555/xiaoqu/roominfo.aspx?dongid=' + dongid + '&roomid=' + roomid
                house = House(co_index)
                house.co_name = 'Labelxqmc">(.*?)<'
                house.area = 'Labelxzq">(.*?)<'
                house.bu_num = 'Labeldongmc">(.*?)<'
                house.ho_type = 'Labelyxyongtu">(.*?)<'
                house.ho_name = '<span id="Labelroommc".*?>(.*?)</span>'
                house.ho_build_size = 'Labeljzmianji">(.*?)<'
                house.ho_true_size = 'Labeltaonei">(.*?)<'
                house.ho_share_size = 'Labelgongtan">(.*?)<'
                house.ho_room_type = 'Labelhuxing">(.*?)<'
                house.bu_id = 'dongid=(.*?)&'
                p = ProducerListUrl(page_url=house_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=house.to_dict(),
                                    analyzer_type='regex',
                                    headers=self.headers)
                p.get_details()
            except Exception as e:
                print('房号错误,co_index={},url={}'.format(co_index, house_url), e)
