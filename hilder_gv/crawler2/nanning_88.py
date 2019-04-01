"""
url = http://www.nnfcxx.com/vipdata/fcj.php?list=xjspf
city :  南宁
CO_INDEX : 88
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '88'
city = '南宁'
log = LogHandler('nanning_88')

class Nanning(Crawler):
    def __init__(self):
        self.start_url = 'http://www.nnfcxx.com/vipdata/fcj.php?list=xjspf'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='cite>.*?/(.*?)页<',
                       )
        page = b.get_page_count()

        for i in range(1,int(page)+1):

            url = self.start_url + '&page=' + str(i)
            res = requests.get(url,headers=self.headers)
            comm_url_list = re.findall("window.open\('(.*?)'\)",res.text,re.S|re.M)
            self.comm_info(comm_url_list)


    def comm_info(self,comm_url_list):
            for comm_url in comm_url_list:
                try:
                    co_res = requests.get(comm_url,headers=self.headers)
                    co = Comm(co_index)
                    co.co_id = re.search('bh=(\d+)',comm_url).group(1)
                    co.co_name = re.search('项目名称.*?td>(.*?)</',co_res.text,re.S|re.M).group(1)
                    co.co_develops = re.search('公司名称.*?strong>(.*?)</s',co_res.text,re.S|re.M).group(1)
                    co.co_address = re.search('项目坐落.*?">(.*?)</',co_res.text,re.S|re.M).group(1)
                    co.co_pre_sale = re.search('预售证号.*?td>(.*?)</',co_res.text,re.S|re.M).group(1)
                    co.co_pre_sale_date = re.search('批准时间.*?td>(.*?)</',co_res.text,re.S|re.M).group(1)
                    co.co_build_size = re.search('预售面积.*?">(.*?)</',co_res.text,re.S|re.M).group(1)
                    co.insert_db()

                    html = etree.HTML(co_res.text)
                    bu_info_list = html.xpath("//tr[@style]")
                except Exception as e:
                    log.error('小区信息错误',e)
                    continue
                self.build_info(bu_info_list,co.co_id)
                bu_url_list = re.findall("window.open\('(.*?)'\)",co_res.text,re.S|re.M)
                self.ho_info(bu_url_list,co.co_id)

    def build_info(self,bu_info_list,co_id):
        for bu_info in bu_info_list:
            try:
                bu = Building(co_index)
                url = bu_info.xpath("./@onclick")[0]
                bu.bu_id = re.search('dbh=(\d+)',url).group(1)
                bu.co_id = co_id
                bu.bu_num = bu_info.xpath("./td[@class='org']/text()")[0]
                bu.bu_all_house = bu_info.xpath("./td[3]/text()")[0]
                bu.size = bu_info.xpath("./td[2]/text()")[0]
                bu.insert_db()
            except Exception as e:
                log.error('楼栋信息错误',e)

    def ho_info(self,bu_url_list,co_id):
        for bu_url in bu_url_list:
            try:
                res = requests.get(bu_url,headers=self.headers)
                html = etree.HTML(res.text)
                house_info_list = html.xpath("//li[@class='tjCor4']")
                for house_info in house_info_list:
                    house = house_info.xpath("./@title")[0]
                    ho = House(co_index)
                    ho.co_id = co_id
                    ho.bu_id = re.search('dbh=(\d+)',bu_url).group(1)
                    ho.ho_name = re.search('房号：(.*?)<br',house).group(1)
                    ho.ho_room_type = re.search('户型：(.*?)<br',house).group(1)
                    ho.ho_build_size = re.search('建筑面积：(.*?)平方米',house).group(1)
                    ho.ho_price = re.search('单价：(.*?)元',house).group(1)
                    ho.ho_type = re.search('用途：(.*?)<br',house).group(1)

                    ho.insert_db()
            except Exception as e:
                log.error('房号信息错误',e)