"""
url = http://www.zyfgj.org/spf/sc_spf_lb.html
city :  资阳
CO_INDEX : 202
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
import json
from lib.log import LogHandler


co_index = '202'
city_name = '资阳'
log = LogHandler("ziyang")

class Ziyang(Crawler):
    def __init__(self):
        self.start_url = 'http://www.zyfgj.org/spf/scspf.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',

        }
        self.proxies = [{"http": "http://192.168.0.96:3234"},
                        {"http": "http://192.168.0.93:3234"},
                        {"http": "http://192.168.0.90:3234"},
                        {"http": "http://192.168.0.94:3234"},
                        {"http": "http://192.168.0.98:3234"},
                        {"http": "http://192.168.0.99:3234"},
                        {"http": "http://192.168.0.100:3234"},
                        {"http": "http://192.168.0.101:3234"},
                        {"http": "http://192.168.0.102:3234"},
                        {"http": "http://192.168.0.103:3234"}, ]

    def start_crawler(self):
        for i in range(1,21):
            data = {
                "page":i,
                "action":'get_spf_list',
                "sort":0
            }
            res = requests.post(self.start_url,data=data,headers=self.headers)
            com_dict = json.loads(res.content.decode())
            for comm in com_dict['list']:
                comm_id = comm['DAH']
                form_data = {
                    "action":"get_spf_info",
                    "dah":comm_id,
                }
                comm_res = requests.post(self.start_url,data=form_data,headers=self.headers)
                self.comm_parse(comm_res,comm_id)
                self.build_parse(comm_id)

    def comm_parse(self,comm_res,co_id):
        comm_dict = json.loads(comm_res.content.decode())
        comm_info = comm_dict["jbxx"]
        co = Comm(co_index)
        co.co_id = co_id
        co.co_name = comm_info["XMMC"]
        co.co_address = comm_info["XMDZ"]
        co.co_develops = comm_info["FDCKFQYMC"]
        co.area = comm_info["QXH_MC"]
        co.co_build_size = comm_info["ZJZMJ"]
        co.co_size = comm_info["ZDMJ"]
        co.insert_db()


    def build_parse(self,co_id):
        bu_url = "http://www.zyfgj.org/spf/GetBTable.ashx"
        bu_data = {
            "itemRecord":co_id,
            "houseCode":0
        }
        res = requests.post(bu_url,data=bu_data,headers=self.headers)
        con = res.content.decode()
        bu_list = re.findall('<tr id.*?</tr>',con)
        for bo in bu_list:
            bu =Building(co_index)
            bu.co_id = co_id
            bu_id = re.search('GetData.*?,(.*?)\)',bo).group(1)
            bu.bu_id = bu_id.strip("'")
            try:
                bu.bu_num = re.search('预售证时间:.*?<td>(.*?)</td',bo).group(1)
                bu.bu_pre_sale = re.search('预售证号:(.*?)</td',bo).group(1)
                bu.bu_pre_sale_date = re.search('预售证时间:(.*?)</td',bo).group(1)
                bu.bu_all_house = re.search('预售证号:.*?<td>(\d+)</td',bo).group(1)
            except Exception as e:
                log.error("{}楼栋无预售号等信息{}".format(bo,e))
            bu.insert_db()
            self.house_parse(co_id,bu.bu_id)

    def house_parse(self,co_id,bu_id):
        ho_url = 'http://www.zyfgj.org/spf/GetBTable.ashx'
        ho_data = {
            "itemRecord": co_id,
            "houseCode": bu_id
        }
        ho_res = requests.post(ho_url,data=ho_data,headers=self.headers)
        con = ho_res.content.decode()
        ho_list = re.findall("<td width='95'.*?</td>",con)
        for ho in ho_list:
            try:
                house = House(co_index)
                house.co_id = co_id
                house.bu_id = bu_id
                house.ho_name = re.search('&nbsp;(.*?)</td',ho).group(1)
                house.ho_build_size = re.search('建筑面积：(.*?)平',ho).group(1)
                house.ho_price = re.search("总价：(.*?)'",ho).group(1)
                house.ho_type = re.search('物业类别：(.*?)\s\s',ho).group(1)
                house.unit = re.search('>(.*?)&',ho).group(1)
                house.insert_db()
            except Exception as e:
                log.error('{}房屋解析错误{}'.format(ho,e))




