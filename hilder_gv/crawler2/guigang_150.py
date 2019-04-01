"""
url = http://www.ggsfcw.com/lpzs.aspx
city :  贵港
CO_INDEX : 150
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House

import re, requests
from lxml import etree

from lib.log import LogHandler

co_index='150'
city = '贵港'
log = LogHandler('guigang_150')

class Guigang(Crawler):
    def __init__(self):
        self.start_url = 'http://www.ggsfcw.com/lpzs.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        html = etree.HTML(res.text)
        comm_url_list = html.xpath("//div[@class='post']//a/@href")
        for comm_url in comm_url_list:
            try:
                url = 'http://www.ggsfcw.com/'+comm_url
                comm_res= requests.get(url,headers=self.headers)
                com_html = etree.HTML(comm_res.text)
                comm = Comm(co_index)
                comm.co_name = re.search('<h3.*?">(.*?)</',comm_res.text).group(1)
                comm.co_id = re.search('n=(\d+)',comm_res.text).group(1)
                comm.co_address = re.search('地址.*?">(.*?)</',comm_res.text).group(1)
                comm.area = re.search('区县.*?">(.*?)</',comm_res.text).group(1)
                comm.co_develops = re.search('开发商.*?">(.*?)</',comm_res.text).group(1)
                comm.co_use = re.search('规划用途.*?">(.*?)</',comm_res.text).group(1)
                comm.insert_db()
            except Exception as e:
                log.error("小区信息错误",e)
                continue

            bu_list = com_html.xpath("//div[@id='MainContent_divResult']/a")
            self.build_info(bu_list,comm.co_id)

    def build_info(self,bu_list,co_id):
        for bo in bu_list:
            ho_url = bo.xpath("./@href")[0]
            floor = bo.xpath(".//p[2]/text()")[0]
            bu = Building(co_index)
            bu.bu_pre_sale = bo.xpath(".//p[3]/text()")[0]
            bu.bu_num = re.search('zh=(.*?)',ho_url).group(1)
            bu.bu_id = re.search('n=(\d+)',ho_url).group(1)
            bu.co_id = co_id
            bu.bu_floor = re.search('总层数.*?(\d+)',floor).group(1)
            bu.insert_db()
            house_url = "http://www.ggsfcw.com/" + ho_url
            self.ho_info(house_url,co_id,bu.bu_id)

    def ho_info(self,house_url,co_id,bu_id):
        res = requests.get(house_url,headers=self.headers)
        html = etree.HTML(res.text)
        ho_info_list = html.xpath("//tbody//td[@unitname]")
        for ho_info in ho_info_list:
            try:
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = ho_info.xpath("./text()")[0]
                ho.insert_db()
            except Exception as e:
                log.error("小区房屋信息提取失败",e)

