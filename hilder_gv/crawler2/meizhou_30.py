"""
    rsa加密
"""

"""
url = http://219.132.136.142:8080/gz/index.asp?skey=&kind=&page=1
city : 梅州
CO_INDEX : 30
小区数量：254
"""

import requests
from lxml import etree
from backup.comm_info import Comm


url = 'http://219.132.136.142:8080/gz/index.asp?skey=&kind=&page=1'
co_index = '30'
city = '梅州'


class Meizhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url)
        html = response.text
        tree = etree.HTML(html)
        area_url_list = tree.xpath('//select[@name="qxrk"]/option/@value')
        self.get_area_info(area_url_list)

    def get_area_info(self, area_url_list):
        print(area_url_list)
        all_comm_list = []
        for i in area_url_list:
            response = requests.get(i)
            html = response.text
            tree = etree.HTML(html)
            comm_page = str(tree.xpath('//td[@valign="bottom"]/a[@class="menu"]/text()')[-1])
            comm_max_page = comm_page.replace('[', '').replace(']', '')
            for num in range(1, int(comm_max_page) + 1):
                detail_comm_url = i + '/?page=' + str(num)
                result = requests.get(detail_comm_url).text
                tree_page = etree.HTML(result)
                comm_url_list = tree_page.xpath('//tr[@bgcolor="white"]/td[@height="22"]/a/@href')
                for comm_url_half in comm_url_list:
                    comm_url = i + '/' + comm_url_half
                    all_comm_list.append(comm_url)
        self.get_comm_info(all_comm_list)
    def get_comm_info(self,all_comm_list):
        for i in all_comm_list:
            comm = Comm(co_index)
            comm.co_name = '企业名称：.*?<TD.*?>(.*?)<'
            comm.co_address = '企业地址：.*?<TD.*?>(.*?)<'
            comm.co_pre_sale = '资质编号：.*?<TD.*?>(.*?)<'
