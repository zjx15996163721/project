"""
url = http://as.gzfcxx.cn/House.aspx
city :  安顺
CO_INDEX : 149
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House

import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '149'
city =  '安顺'
log = LogHandler('anshun_149')

class Anshun(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.start_url = 'http://as.gzfcxx.cn/House.aspx'
    def start_crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        page_num = re.findall('(\d+)">末页',res.text)[0]
        for i in range(1,int(page_num)+1):
            url = self.start_url + "?page=" + str(i)
            page_res = requests.get(url,headers=self.headers)
            html = etree.HTML(page_res.text)
            comm_url_list = html.xpath("//div[@align='left']/a[@class='url']/@href")
            self.comm_info(comm_url_list)

    def comm_info(self,comm_url_list):
        for comm_url in comm_url_list:
            try:
                url = "http://as.gzfcxx.cn"+comm_url
                res =requests.get(url,headers=self.headers)
                co = Comm(co_index)
                co.co_name = re.search('项目名称.*?ck">(.*?)<',res.text,re.S|re.M).group(1)
                co.co_id = re.search('yszh=(\d+)',comm_url).group(1)
                co.co_develops = re.search('开发商.*?ck">(.*?)<',res.text,re.S|re.M).group(1)
                co.co_address = re.search('坐落.*?ck">(.*?)<',res.text,re.S|re.M).group(1)
                co.co_pre_sale = re.search('许可证.*?ck">(.*?)<',res.text,re.S|re.M).group(1)
                co.co_handed_time = re.search('交房时间.*?ck">(.*?)<',res.text,re.S|re.M).group(1)
                co.insert_db()

                html = etree.HTML(res.text)
                build_detail = html.xpath("//a[@class='a3']/@href")[0]
            except Exception as e:
                log.error('小区信息错误',e)
                continue
            self.build_info(build_detail,co.co_id)

    def build_info(self,build_detail,co_id):
        build_detail_url = 'http://as.gzfcxx.cn' + build_detail
        res = requests.get(build_detail_url,headers=self.headers)
        html = etree.HTML(res.text)
        build_info_list = html.xpath("//div[@class='box']//font/a/@href")
        for build_url in build_info_list:
            try:
                url = 'http://as.gzfcxx.cn'+build_url
                ho_res = requests.get(url,headers=self.headers)
                ho_html = etree.HTML(ho_res.text)
                bu = Building(co_index)
                bu.co_id = co_id
                bu.bu_id = re.search('dongID=(\d+)',build_url).group(1)
                bu.bu_num = ho_html.xpath("//option[@selected='selected']/text()")[0]
                bu.insert_db()
                temp  = re.search("\?(.*?dongID=\d+)", build_url).group(1)
                real_url = 'http://as.gzfcxx.cn/Controls/HouseControls/FloorView.aspx?' + temp
                house_res = requests.get(real_url,headers=self.headers)
                ho_html = etree.HTML(house_res.text)
                info = ho_html.xpath("//table[@class='C1 T0 F0']/..")
            except Exception as e:
                log.error('楼栋信息错误',e)
                continue
            for i in info:
                try:
                    ho = House(co_index)
                    ho_info = i.xpath("./@title")[0]
                    ho.ho_build_size = re.search('(\d+).(\d+)',ho_info,re.S|re.M).group(1)
                    ho.ho_name = i.xpath(".//span/text()")[0]
                    ho.bu_id = bu.bu_id
                    ho.co_id = co_id
                    ho.insert_db()
                except Exception as e:
                    log.error('房间信息错误',e)




