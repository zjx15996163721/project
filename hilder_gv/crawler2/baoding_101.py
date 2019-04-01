"""
url = http://www.bdfdc.net/loadAllProjects.jspx
city :  保定
CO_INDEX : 101
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
import time
from lib.log import LogHandler

co_index = '101'
city = '保定'

log = LogHandler('baoding_101')

class Baoding(Crawler):
    def __init__(self):
        self.start_url = 'http://www.bdfdc.net/loadAllProjects.jspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='共(\d+)页',
                       )
        page = b.get_page_count()
        for i in range(1,int(page)+1):
            url = self.start_url + '?pageIndex=2' + str(page)
            page_res = requests.get(url,headers=self.headers)

            html = etree.HTML(page_res.text)
            comm_info_list = html.xpath("//ul/li/div")
            for comm_info in comm_info_list:
                try:
                    co = Comm(co_index)
                    co.co_name = comm_info.xpath("./p/a/text()")[0]
                    deve = comm_info.xpath("./p[2]/text()")[0]
                    addr = comm_info.xpath("./p[3]/text()")[0]
                    co.co_develops = re.search('开发商:(.*)',deve).group(1)
                    co.co_address = re.search('楼盘地址.*?:(.*)',addr).group(1)
                    comm_url = comm_info.xpath("./p/a/@href")[0]
                    co.co_id = re.search('projectId=(\d+)',comm_url).group(1)
                    co.insert_db()
                    co_url = 'http://www.bdfdc.net' + comm_url
                    co_res = requests.get(co_url,headers=self.headers)
                    time.sleep(5)
                    bu_html = etree.HTML(co_res.text)
                    bu_url_list = bu_html.xpath("//div[@style]/a")[1:]
                except Exception as e:
                    # log.error("小区信息错误{}".format(e))
                    print("小区信息错误{}".format(e))
                    continue
                self.bu_info(bu_url_list,co.co_id)

    def bu_info(self,bu_url_list,co_id):
        for bu_ in bu_url_list:
            try:
                bu = Building(co_index)
                bu.co_id = co_id
                bu.bu_num = bu_.xpath("./text()")[0]
                bu_url = bu_.xpath("./@href")[0]
                bu.bu_id = str(co_id) + str(re.search('build=(\d+)',bu_url).group(1))
                bu.insert_db()
            except Exception as e:
                # log.error("楼栋信息错误{}".format(e))
                print("楼栋信息错误{}".format(e))
                continue
            try:
                self.house_info(co_id,bu.bu_id,bu_url)
            except Exception as e:
                # log.error("房屋信息错误{}".format(e))
                print("房屋信息错误{}".format(e))
                continue


    def house_info(self,co_id,bu_id,bu_url):

        ho_url = 'http://www.bdfdc.net' + bu_url
        res = requests.get(ho_url,headers=self.headers)
        time.sleep(5)
        html = etree.HTML(res.text)
        house_info_list = html.xpath("//a[@wf]")
        for house_info in house_info_list:
            ho = House(co_index)
            detail = house_info.xpath("./@wf")[0]
            ho.ho_name = house_info.xpath("./text()")[0]
            ho.bu_id = bu_id
            ho.co_id = co_id
            ho.ho_build_size = re.search('建筑面积:(.*?)m',detail).group(1)
            ho.ho_type = re.search('用途:(.*?)<br',detail).group(1)
            ho.insert_db()
