"""
url = gold.ncfdc.com.cn/Default.aspx?tname=251%5cmain
city : 南昌
CO_INDEX : 31
小区数量：254
"""

import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
import re

url = 'http://gold.ncfdc.com.cn/Default.aspx?tname=251%5cmain'
co_index = '31'
city = '南昌'


class Nanchang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url)
        html = response.text
        tree = etree.HTML(html)
        all_comm_url = tree.xpath('//div[@class="lpda_pinyin"]/a/@href')
        self.get_comm_info(all_comm_url)

    def get_comm_info(self, all_comm_url):
        for i in all_comm_url:
            try:
                comm = Comm(co_index)
                comm_url = 'http://gold.ncfdc.com.cn/' + i
                res = requests.get(comm_url, headers=self.headers)
                comm.co_name = re.search('ctl15_proname">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_address = re.search('ctl20_ADDRESS">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_develops = re.search('ctl20_developer_name">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_build_size = re.search('ctl20_build_area">(.*?)<', res.text, re.S | re.M).group(1)
                comm.area = re.search('ctl20_region_name">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_type = re.search('ctl20_PropertyType">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_green = re.search('ctl20_VIRESCENCE">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_volumetric = re.search('ctl20_PLAT_RATIO">(.*?)<', res.text, re.S | re.M).group(1)
                comm.co_id = re.search('name="form1.*?hrefID=(.*?)"', res.text, re.S | re.M).group(1)
                comm.insert_db()

                build_url_list = []
                for j in re.findall('doc_nav_LD" href="(.*?)"', res.text, re.S | re.M):
                    build_url_list.append(j)
                self.get_build_info(build_url_list, comm.co_id)

            except Exception as e:
                print('小区错误，co_index={}, url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url_list, co_id):
        for i in build_url_list:

            build_url = 'http://gold.ncfdc.com.cn/' + i.replace('amp;', '')
            res = requests.get(build_url)

            co_name = re.search('ctl15_proname">(.*?)<', res.text, re.S | re.M).group(1)
            str = re.search('项目楼栋列表.*?ctl17_fLinks_pDataShow', res.text, re.S | re.M).group()
            for info in re.findall('<tr>.*?</tr>', str, re.S | re.M):
                if 'href' not in info:
                    continue
                try:
                    build = Building(co_index)
                    build.co_name = co_name
                    build.bu_num = re.search('<tr>.*?<td>.*?<a href=.*?>(.*?)<', info, re.S | re.M).group(1)
                    build.bu_pre_sale = re.search('onclick="BinSHouseInfo.*?>(.*?)<', info, re.S | re.M).group(1)
                    build.bu_pre_sale_date = re.search('onclick="BinSHouseInfo.*?<td>(.*?)<', info, re.S | re.M).group(
                        1)
                    build.bu_all_house = re.search('color:#ec5f00;">(.*?)<', info, re.S | re.M).group(1)
                    build.bu_id = re.search("DisplayB_ld&hrefID=(.*?)'", info, re.S | re.M).group(1)
                    build.co_id = co_id
                    build.insert_db()

                except Exception as e:
                    print('楼栋错误，co_index={},url={}'.format(co_index, build_url), e)
            house_url_list = re.findall("</span>.*?</td><td>.*?<a href='(.*?xs.*?)' target=\"_blank\">.*?查看", res.text,
                                        re.S | re.M)

            self.get_house_info(house_url_list)

    def get_house_info(self, house_url_list):
        for url in house_url_list:
            response = requests.get(url)

            html = etree.HTML(response.text)
            con = html.xpath("//tr[@align='center']")
            for i in con:
                try:
                    house = House(co_index)
                    # house.ho_num = 'NHOUSENO">(.*?)<'
                    house.ho_name = i.xpath("./td/text()")[1]
                    house.ho_floor = i.xpath("./td/text()")[0]
                    house.ho_build_size = i.xpath("./td/text()")[3]
                    house.ho_true_size = i.xpath("./td/text()")[4]
                    house.ho_share_size = i.xpath("./td/text()")[5]
                    house.ho_room_type = i.xpath("./td/text()")[2]
                    house.ho_price = i.xpath("./td/text()")[-1]
                    house.orientation = i.xpath("./td/text()")[-2]
                    house.bu_id = re.search('ID=(\d+)',url).group(1)
                    house.insert_db()
                except Exception as e:
                    print('房号错误，co_index={},url={}'.format(co_index, url), e)
