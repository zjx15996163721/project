"""
url = http://www.cxsfdcglzx.com/touming/wangShangHouse.aspx
city : 慈溪
CO_INDEX : 8
author: 吕三利
小区数量 : 1901    2018/2/24
"""

from backup.crawler_base import Crawler
from lxml import etree
from backup.comm_info import Comm, Building, House
import requests, re
from retry import retry
import yaml

setting = yaml.load(open('config_local.yaml'))
co_index = 8

class Cixi(Crawler):
    def __init__(self):
        self.url = 'http://www.cxsfdcglzx.com/touming/wangShangHouse.aspx'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }

    def start_crawler(self):
        self.start()

    def is_none(self, xpath_adv):
        if xpath_adv:
            xpath_adv = xpath_adv[0]
        else:
            xpath_adv = None
        return xpath_adv

    @retry(retry(3))
    def start(self):
        response = requests.get(self.url, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        comm_url_list = tree.xpath('//ul[@class="NewsList"]/li/a/@href')
        for i in range(len(comm_url_list)):
            comm = Comm(8)
            comm_url = 'http://www.cxsfdcglzx.com/touming/' + comm_url_list[i]
            print(comm_url)
            self.get_comm_info(comm_url, comm)

    @retry(retry(3))
    def get_comm_info(self, comm_url, comm):
        try:
            response = requests.get(comm_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            co_address = tree.xpath('//*[@id="PageB_Location"]/text()')[0]  # 小区地址
            co_name = re.search('id="PageB_ItemName".*?>(.*?)<', html, re.S | re.M).group(1)
            co_develops = tree.xpath('//*[@id="PageB_CompName"]/text()')[0]  # 开发商
            co_pre_sale = tree.xpath('//*[@id="PageB_PermitNo"]/text()')[0]  # 预售证书
            co_build_end_time = tree.xpath('//*[@id="PageB_FinishDate"]/text()')[0]  # 竣工时间
            co_build_size = tree.xpath('//*[@id="PageB_BuildArea"]/text()')[0]  # 建筑面积
            build_url_list = tree.xpath('//*[@id="Content"]/div[3]/div/div[4]/div[3]/table[2]/tr/td[1]/a/@href')
            comm.co_address = co_address
            comm.co_develops = co_develops
            comm.co_pre_sale = co_pre_sale
            comm.co_build_end_time = co_build_end_time
            comm.co_build_size = co_build_size
            comm.co_name = co_name
            co_id = re.search('aspx\?(.*?)$', comm_url).group(1)
            comm.co_id = co_id
            comm.insert_db()
            for i in build_url_list:
                url = 'http://www.cxsfdcglzx.com/touming/' + i
                print(url)
                self.get_build_info(url, co_id)
        except BaseException as e:
            print(e)

    @retry(retry(3))
    def get_build_info(self, url, co_id):
        try:
            building = Building(co_index)
            response = requests.get(url)
            html = response.text
            tree = etree.HTML(html)
            co_name = tree.xpath('//*[@id="PageB_Location"]/text()')[0]  # 小区名字
            print(co_name)
            bu_name = tree.xpath('//*[@id="ItemName"]/text()')[0]  # 楼栋名称
            bu_num = tree.xpath('//*[@id="PageB_HouseNo"]/text()')[0]  # 楼号 栋号
            bu_all_house = tree.xpath('//*[@id="lb_countbulidtaoshu"]/text()')[0]  # 总套数
            bu_floor = tree.xpath('//*[@id="cell3-1"]/text()')
            bu_floor = self.is_none(bu_floor)  # 楼层
            bu_build_size = tree.xpath('//*[@id="lb_countbulidarea"]/text()')[0]  # 建筑面积
            bu_live_size = tree.xpath('//*[@id="lb_buildarea"]/text()')[0]  # 住宅面积
            bu_price = tree.xpath('//*[@id="lb_buildavg"]/text()')
            bu_price = self.is_none(bu_price)  # 住宅价格
            bu_id = re.search('\?(\d+)$', url).group(1)  # 楼栋id
            building.co_id = co_id
            building.bu_name = bu_name
            building.bu_num = bu_num
            building.bu_all_house = bu_all_house
            building.bu_floor = bu_floor
            building.bu_build_size = bu_build_size
            building.bu_live_size = bu_live_size
            building.bu_price = bu_price
            building.bu_id = bu_id
            building.insert_db()
            house_info_html = re.findall('<tr id="row3">(.*)$', html, re.S | re.M)[0]
            for i in re.findall('(<td.*?>.*?</td>)', house_info_html, re.S | re.M):
                if '<br>' not in i:
                    continue
                ho_name_list = re.findall('<td.*?>(.*?)<br>', i, re.S | re.M)
                ho_true_size_list = re.findall('<td.*?>.*?<br>(.*?)<br>', i, re.S | re.M)
                ho_type = re.findall('<td.*?>.*?<br>.*?<br>(.*?)<br>', i, re.S | re.M)[0]
                for i in range(len(ho_name_list)):
                    try:
                        if 'font' in ho_name_list[i]:
                            ho_name = re.sub('<font.*?>', '', ho_name_list[i])
                        else:
                            ho_name = ho_name_list[i]
                        house = House(8)
                        house.ho_name = ho_name
                        house.ho_true_size = ho_true_size_list[i]
                        house.co_id = co_id
                        house.bu_id = bu_id
                        house.ho_type = ho_type
                        house.insert_db()

                    except Exception as e:
                        print(e)
        except BaseException as e:
            print(e)
