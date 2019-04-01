"""
url = http://fcjwq.maoming.gov.cn:7800/user_kfs.aspx
city :  茂名
CO_INDEX : 187
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree
from backup.proxy_connection import Proxy_contact

co_index = '187'
city_name = '茂名'

class Maoming(Crawler):
    def __init__(self):

        self.start_url ='http://fcjwq.maoming.gov.cn:7800'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer':'http://fcjwq.maoming.gov.cn:7800/user_itemlist.aspx'
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
        page = 0
        while True:
            page +=1
            url = self.start_url + "/user_itemlist.aspx?page=" + str(page)
            res =requests.get(url,headers=self.headers)
            res.encoding = 'gbk'
            if '找不到相关信息' in res.text:
                break
            else:
                html = etree.HTML(res.text)
                url_list = html.xpath("//td[@align='center']/a/@href")
                for url in url_list:
                    self.comm_info(url)

    def comm_info(self,url):
        comm_url = self.start_url + "/" + url
        res = requests.get(comm_url,headers=self.headers)
        res.encoding = 'gbk'
        con = res.text
        co = Comm(co_index)
        co.co_id = re.search('kfsid=(\d+)',url).group(1)
        co.co_name = re.search('itemname.*?">(.*?)</font',con).group(1)
        co.co_develops = re.search('开发商名称：.*?px;">(.*?)</a',con,re.S|re.M).group(1)
        co.co_all_house = re.search('总套数：.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
        co.co_all_size = re.search('总面积：.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
        co.co_residential_size = re.search('>住宅面积：.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
        co.co_address = re.search('项目座落.*?;">(.*?)</',con,re.S|re.M).group(1)
        co.area = re.search('所在地区.*?">(.*?)</td',con,re.S|re.M).group(1)
        try:
            co.co_build_size = re.search('建筑面积.*?">(.*?)&nbsp', con, re.S | re.M).group(1)
            co.co_plan_project = re.search('建设工程规划许可证号.*?">(.*?)<br',con,re.S|re.M).group(1)
            co.co_land_use = re.search('土地证号.*?">(.*?)<br',con,re.S|re.M).group(1)
            co.co_work_pro = re.search('建筑工程施工许可证号.*?">(.*?)<br',con,re.S|re.M).group(1)
            co.co_use = re.search('用途.*?">(.*?)<br',con,re.S|re.M).group(1)
        except:
            co.co_build_size = None
            co.co_plan_project = None
            co.co_land_use = None
            co.co_work_pro = None
            co.co_us = None

        co.insert_db()
        co_html = etree.HTML(con)
        bu_list = co_html.xpath("//table[@id='preselltable1']/tr[@bgcolor='white']")
        self.build_info(bu_list,co.co_id)

    def  build_info(self,bu_list,co_id):
        for bu in bu_list:
            bu_url = bu.xpath("./td[4]/a/@href")[0]
            build_url = self.start_url+'/' + bu_url
            bu_res = requests.get(build_url,headers=self.headers)
            bu_res.encoding = 'gbk'
            con = bu_res.text
            bu_pre_sale = re.search('预售许可证编号.*?blank">(.*?)</a',con,re.S|re.M).group(1)
            bu_pre_sale_date = re.search('预售证有效日期.*?">(.*?)</td',con,re.S|re.M).group(1)

            bu_html = etree.HTML(con)
            donglist = bu_html.xpath("//table[@id='donglist']/tr")
            for dong in donglist:
                dong_url = dong.xpath("./td/a/@href")[0]
                bu = Building(co_index)
                bu.co_id = co_id
                bu.bu_id = re.search('ID={(.*?)}',dong_url).group(1)
                bu.bu_num = dong.xpath("./td[3]/text()")[0]
                bu.bu_floor = dong.xpath("./td[4]/text()")[0]
                bu.bu_pre_sale = bu_pre_sale
                bu.bu_pre_sale_date = bu_pre_sale_date
                bu.insert_db()
                self.house_info(co_id,bu.bu_id,dong_url)

    def house_info(self,co_id,bu_id,dong_url):
        url = self.start_url + "/" +dong_url
        res = requests.get(url,headers=self.headers)
        res.encoding = 'gbk'
        con = res.text
        house_list = re.findall('房屋号.*?<a href="(.*?)"',con,re.S|re.M)
        for house in house_list:
            house_url = self.start_url + "/" + house
            # while True:
            #     try:
            #         proxy = self.proxies[random.randint(0,9)]
            #         ho_res = requests.get(house_url,headers=self.headers,proxies=proxy)
            #         if ho_res.status_code == 200:
            #             break
            #     except:
            #         continue
            # ho_res.encoding = 'gbk'
            # ho_con = ho_res.text
            connect = Proxy_contact(app_name='maoming',method='get',url=house_url,headers=self.headers)
            content = connect.contact()
            if content is False:
                continue
            ho_con = content.decode('gbk')
            try:
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = re.search('房屋号.*?">(.*?)</',ho_con,re.S|re.M).group(1)
                ho.ho_true_size = re.search('套内面积.*?">(.*?)m',ho_con,re.S|re.M).group(1)
                ho.ho_build_size = re.search('建筑面积.*?">(.*?)m',ho_con,re.S|re.M).group(1)
                ho.ho_type = re.search('房屋用途.*?">(.*?)<',ho_con,re.S|re.M).group(1)
                ho.ho_price = re.search('申报总价.*?">(.*?)<',ho_con,re.S|re.M).group(1)
                ho.orientation = re.search('朝向.*?">(.*?)<',ho_con,re.S|re.M).group(1)
                ho.insert_db()
            except Exception as e:
                print("房屋解析失败",e)

