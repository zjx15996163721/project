"""
url = http://110.89.45.7:8082/
city :  莆田
CO_INDEX : 188
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
import random
import time

co_index = '188'
city_name = '莆田'

class Putian(Crawler):
    def __init__(self):
        self.start_url = 'http://110.89.45.7:8082/House/ListCanSell_Stats?place='
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            # 'Referer': ''
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
        self.region_list = ['城厢区','荔城区','涵江区','秀屿区']

    def start_crawler(self):
        for region in self.region_list:
            region_url = self.start_url + region
            b = AllListUrl(first_page_url=region_url,
                           request_method='get',
                           analyzer_type='regex',
                           encode='utf-8',
                           page_count_rule='1/(\d+)页',
                           )
            page = b.get_page_count()
            for i in range(1,int(page)+1):
                url = region_url + "&pagenumber=" + str(i)
                res = requests.get(url,headers=self.headers)
                html = etree.HTML(res.text)
                url_list = html.xpath("//tr/td/a/@href")
                self.comm_parse(url_list,region)
    def comm_parse(self,url_list,region):
        for co_url in url_list:
            comm_url = "http://110.89.45.7:8082" + co_url
            comm_res = requests.get(comm_url,headers=self.headers)
            con = comm_res.text
            co = Comm(co_index)
            co.co_id = re.search('ProjectId=(.*)',co_url).group(1)
            co.co_name = re.search('项目名称.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.co_develops = re.search('公司名称.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.co_address = re.search('项目坐落.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.co_use = re.search('规划用途.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.co_build_size = re.search('建筑面积.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.area = region
            co.co_residential_size = re.search('批准销售.*?">.*?</td.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.co_pre_sale = re.search('预售许可证.*?">(.*?)</td',con,re.S|re.M).group(1)
            co.insert_db()
            co_html = etree.HTML(comm_res.text)
            bu_urllist = co_html.xpath("//span/a/@href")
            self.bu_parse(co.co_id,bu_urllist)

    def bu_parse(self,co_id,bulist):
        for bo in bulist:
            bu_url = "http://110.89.45.7:8082" + bo
            bu_res = requests.get(bu_url,headers=self.headers)
            con = bu_res.text
            bu = Building(co_index)
            bu.co_id = co_id
            bu.bu_id = re.search('buildingInfoID=(.*?)&',bo).group(1)
            bu.bu_num = re.search('幢号.*?">(.*?)</',con,re.S|re.M).group(1)
            bu.bu_floor = re.search('总 层 数.*?">(.*?)</',con,re.S|re.M).group(1)
            bu.bu_live_size = re.search('批准销售.*?">.*?</td.*?">(.*?)</td',con,re.S|re.M).group(1)
            bu.bu_all_size = re.search('总面积.*?">(.*?)</',con,re.S|re.M).group(1)
            bu.bu_type = re.search('设计用途.*?">(.*?)</',con,re.S|re.M).group(1)
            bu.insert_db()

            bu_html = etree.HTML(con)
            ho_list = bu_html.xpath("//td[@style]/a")
            self.ho_parse(co_id,bu.bu_id,ho_list)

    def ho_parse(self,co_id,bu_id,ho_list):
        for ho in ho_list:
            ho_url = ho.xpath("./@href")[0]
            house_url = "http://110.89.45.7:8082"+ho_url
            # while True:
            #     try:
            #         proxy = self.proxies[random.randint(0,9)]
            try:
                ho_res = requests.get(house_url,headers=self.headers,)
            except:
                continue
                #     break
                # except:
                #     continue
            con = ho_res.text
            house = House(co_index)
            house.co_id = co_id
            house.bu_id = bu_id
            house.ho_name = re.search('房　　号.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.ho_build_size =  re.search('建筑面积.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.ho_true_size = re.search('套内面积.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.ho_share_size = re.search('分摊面积.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.ho_floor = re.search('所 在 层.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.ho_price = re.search('申报单价.*?">(.*?)</td',con,re.S|re.M).group(1)
            house.ho_type = re.search('房屋用途.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            house.insert_db()
            time.sleep(random.randint(0,3))



