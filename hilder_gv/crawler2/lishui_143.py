"""
url = http://www.lsjs.gov.cn/WebLSZFGB/showInfo/lpmore.htm
city :  丽水
CO_INDEX : 143
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree
import json
from lib.log import LogHandler

co_index = '143'
city_name = '丽水'
log = LogHandler('lishui_143')

class Lishui(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            # 'Cookie': 'yd_cookie=fea22237-25bd-485c9e7057ae1b5651008732799d98327d88; __CSRFCOOKIE=5bb064f4-3860-4f32-8e20-e2e46a325295',
            'Host': 'www.lsjs.gov.cn',
            'Origin': 'http://www.lsjs.gov.cn',
            # 'Referer': 'http://www.lsjs.gov.cn/WebLSZFGB/showInfo/lpmore.htm'
        }

        self.start_url = 'http://www.lsjs.gov.cn/WebLSZFGB/showInfo/lpmore.htm'
    def start_crawler(self):

        url = 'http://www.lsjs.gov.cn/WebLSZFGB/Ashx/YSXM.ashx'
        count = 1
        while True:
            data = {
                "method": "getlpxxpage",
                "PageSize": "20",
                "CurrentPageIndex": str(count),
                "XZQH": "0",
                "Searchkey":'',
            }
            res = requests.post(url,data=data,headers=self.headers)
            con_dict = json.loads(res.text)
            num = con_dict["data"][0]['TotalNum']
            info_list = con_dict["data"][1:]
            for info in info_list:
                co_id = info["YSXMID"]
                self.comm_info(co_id)
            if int(num) < count*20:
                break
            else:
                count += 1
                continue

    def comm_info(self,co_id):
        comm_url = "http://www.lsjs.gov.cn/WebLSZFGB/LPDetail.aspx?RowGuid=" + co_id
        co_res = requests.get(comm_url,headers=self.headers)
        con = co_res.text
        co = Comm(co_index)
        co.co_name = re.search('楼 盘 名 称：(.*?)<br',con).group(1)
        co.co_id = co_id
        co.area = re.search('所 属 城 区：.*?">(.*?)</span',con).group(1)
        co.co_address = re.search('楼 盘 坐 落：.*?">(.*?)</span',con).group(1)
        co.co_develops = re.search('项 目 公 司：.*?mc">(.*?)</span',con,re.S|re.M).group(1)
        co.co_pre_sale = re.search('预销售证号.*?">(.*?)</span',con,re.S|re.M).group(1)
        co.co_all_house = re.search('预售总套数.*?td>(.*?)</td',con,re.S|re.M).group(1)
        co.co_all_size = re.search('预售总面积.*?td>(.*?)</td',con,re.S|re.M).group(1)
        co.co_pre_sale_date = re.search('时间.*?">(.*?)</span',con,re.S|re.M).group(1)
        co.insert_db()

        url = 'http://www.lsjs.gov.cn/WebLSZFGB/Ashx/YSXM.ashx'
        count = 1
        while True:
            data = {
                "method": "getzxl",
                "PageSize": 5,
                "CurrentPageIndex": str(count),
                "YSXMID": co_id,
                # 'Searchkey':''
            }
            res = requests.post(url, data=data, headers=self.headers)
            con_dict = json.loads(res.text)
            num = con_dict["data"][0]['TotalNum']
            info_list = con_dict["data"][1:]
            for info in info_list:
                bu_id = info["YSZID"]
                self.build_info(co_id,bu_id)
            if int(num) < count * 5:
                break
            else:
                count += 1
                continue

    def build_info(self,co_id,bu_id):
        bu_url = 'http://www.lsjs.gov.cn/WebLSZFGB/ZNInfo.aspx?YSZID=' + bu_id + "&YSXMID=" + co_id
        bu_res = requests.get(bu_url,headers=self.headers)
        con = bu_res.text
        bu =Building(co_index)
        bu.co_id = co_id
        bu.bu_id = bu_id
        bu.bu_num = re.search('znxx">(.*?)</span',con).group(1)
        bu.bu_all_house = re.search('纳入网上预（销）售总套数.*?">(.*?)</',con,re.S|re.M).group(1)
        bu.bu_build_size = re.search('纳入网上预（销）售总面积.*?">(.*?)</',con,re.S|re.M).group(1)
        bu.insert_db()

        html = etree.HTML(con)
        house_list = html.xpath("//span[@class='syt-span']")
        for tag in house_list:
            ho =House(co_index)
            ho.bu_id = bu_id
            ho.co_id = co_id
            ho.ho_name = tag.xpath(".//p[@class='ewb-num']/text()")[0]
            ho.ho_build_size = tag.xpath(".//p[@class='ewb-con']/text()")[0]
            ho.insert_db()
