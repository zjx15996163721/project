"""
url = http://www.czfdc.gov.cn/spf/gs.php
city : 池州
CO_INDEX : 6
author: 吕三利
小区数量：18页   2018/2/22
"""

from backup.crawler_base import Crawler
from lxml import etree
from backup.comm_info import Comm, Building, House
import requests, re
from retry import retry


class Chizhou(Crawler):
    def __init__(self):
        self.co_index = 6
        self.url = 'http://www.czfdc.gov.cn/spf/gs.php'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }

    def start_crawler(self):
        self.start()

    @retry(retry(3))
    def get_all_page(self):
        response = requests.get(url=self.url, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        page = tree.xpath('//div[@id="page_list"]/a/span/text()')[-1]
        print('co_index={},page={}'.format(self.co_index, page))
        return page

    def is_none(self, xpath_adv):
        if xpath_adv:
            xpath_adv = xpath_adv[0]
        else:
            xpath_adv = None
        return xpath_adv

    @retry(retry(3))
    def start(self):
        page = self.get_all_page()
        count = 0
        for i in range(1, int(page) + 1):
            try:
                url = 'http://www.czfdc.gov.cn/spf/gs.php?pageid=' + str(i)
                response = requests.get(url, headers=self.headers)
                html = response.content.decode('gbk')
                tree = etree.HTML(html)
                comm_url_list = tree.xpath('//td[@align="left"]/a/@href')

                for j in comm_url_list:
                    count += 1
                    print(count)
                    comm = Comm(6)
                    comm_url = 'http://www.czfdc.gov.cn/spf/' + j
                    self.get_comm_info(comm_url, comm)
            except Exception as e:
                print('co_index={},翻页有问题，url={}'.format(self.co_index, url), e)
                continue

    @retry(retry(3))
    def get_comm_info(self, comm_url, comm):
        try:
            response = requests.get(comm_url, headers=self.headers)
            html = response.content.decode('gbk')
            tree = etree.HTML(html)
            # 小区id
            co_id = re.search('id=(\d+?)$', comm_url).group(1)
            # 小区地址
            co_address = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[4]/tr[1]/td[2]/text()')
            co_address = self.is_none(co_address)
            # 小区名称
            co_name = tree.xpath(
                '//*[@id="main"]/table/tr/td[2]/table[2]/tr/td[2]/table/tr/td/strong/text()')
            co_name = self.is_none(co_name)
            # 小区总套数
            co_all_house = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[4]/tr[7]/td[2]/text()')
            co_all_house = self.is_none(co_all_house)
            # 预售证书
            # co_pre_sale = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[4]/tr[4]/td[2]/a/text()')
            pre_sale_str = re.search('预售许可证号：(.*?)开发商名称：',html,re.S | re.M).group(1)
            co_pre_sale = []
            for pre_sale in re.findall("_blank'>(.*?)<", pre_sale_str, re.S | re.M):
                co_pre_sale.append(pre_sale)

            # 开发商
            co_develops = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[4]/tr[5]/td[2]/a/text()')
            co_develops = self.is_none(co_develops)
            # 占地面的
            co_size = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[4]/tr[8]/td[2]/text()')
            co_size = self.is_none(co_size)
            comm.co_id = co_id
            comm.co_address = co_address
            comm.co_name = co_name
            comm.co_all_house = co_all_house
            comm.co_pre_sale = co_pre_sale
            comm.co_develops = co_develops
            comm.co_size = co_size
            comm.insert_db()

            build_url = tree.xpath('//*[@id="main"]/table/tr/td[2]/table[1]/tr/td[1]/a/@href')
            build_url = self.is_none(build_url)
            build_url = 'http://www.czfdc.gov.cn/spf/' + build_url
            self.get_build_info(build_url, co_id)
            # 插入数据库
        except Exception as e:
            print('co_index={},小区错误，url='.format(self.co_index, comm_url), e)

    @retry(retry(3))
    def get_build_info(self, build_url, co_id):
        try:
            response = requests.get(build_url, headers=self.headers)
            html = response.content.decode('gbk')
            tree = etree.HTML(html)
            bu_detail_url = tree.xpath('/html/body/table/tr/td/table/tr/td/table[1]/tr/td[1]/input/@onclick')
            for i in bu_detail_url:
                building = Building(6)
                bu_detail_url = re.search("location='(.*?)'", i).group(1)
                bu_detail_url = 'http://www.czfdc.gov.cn/spf/' + bu_detail_url

                self.get_build_detail_info(bu_detail_url, building, co_id)

        except Exception as e:
            print('co_index={},楼栋url，url={}'.format(self.co_index, build_url), e)

    @retry(retry(3))
    def get_build_detail_info(self, bu_detail_url, building, co_id):
        try:
            response = requests.get(bu_detail_url, headers=self.headers)
            html = response.content.decode('gbk')
            tree = etree.HTML(html)
            # 楼层
            bu_floor = tree.xpath('/html/body/table[4]/tr/td/table[2]/tr[2]/td[1]/text()')
            bu_floor = self.is_none(bu_floor).strip()
            # 总套数
            bu_all_house = tree.xpath('/html/body/table[2]/tr/td[1]/table[1]/tr[3]/td[1]/text()')
            bu_all_house = self.is_none(bu_all_house).replace('套(间)', '')
            # 楼栋名称
            bu_name = tree.xpath('/html/body/table[3]/tr/*/*/*/*/option[@selected]/text()')
            bu_name = self.is_none(bu_name)
            # 楼栋id
            bu_id = re.search('buildid=(\d+?)&', bu_detail_url).group(1)
            building.bu_floor = bu_floor
            building.bu_all_house = bu_all_house
            building.bu_name = bu_name
            building.bu_id = bu_id
            building.co_id = co_id
            # 插入数据库
            building.insert_db()

            house_url_list = tree.xpath('/html/body/table[4]/tr/td/table[2]/tr/td[not(@bgcolor="#ffffff")]/a/@href')
            for i in house_url_list:
                house = House(6)
                house_url = 'http://www.czfdc.gov.cn/spf/' + i
                self.get_house_info(house_url, house, co_id, bu_id)
            return building
        except Exception as e:
            print('co_index={},楼栋错误,url={}'.format(self.co_index, bu_detail_url), e)

    @retry(retry(3))
    def get_house_info(self, house_url, house, co_id, bu_id):
        try:
            response = requests.get(house_url, headers=self.headers)
            html = response.content.decode('gbk')
            tree = etree.HTML(html)
            ho_name = tree.xpath('/html/body/table/tr[2]/td[4]/text()')
            if not ho_name:
                return
            ho_name = self.is_none(ho_name)
            ho_floor = tree.xpath('/html/body/table/tr[2]/td[2]/text()')
            ho_floor = self.is_none(ho_floor).replace('层', '')
            ho_price = tree.xpath('/html/body/table/tr[6]/td[2]/text()')
            ho_price = self.is_none(ho_price)
            ho_build_size = tree.xpath('/html/body/table/tr[4]/td[2]/text()')
            ho_build_size = self.is_none(ho_build_size).replace('m', '')
            ho_true_size = tree.xpath('/html/body/table/tr[4]/td[4]/text()')
            ho_true_size = self.is_none(ho_true_size).replace('m', '')
            ho_share_size = tree.xpath('/html/body/table/tr[5]/td[2]/text()')
            ho_share_size = self.is_none(ho_share_size).replace('m', '')
            ho_room_type = tree.xpath('/html/body/table/tr[3]/td[4]/text()')
            ho_room_type = self.is_none(ho_room_type)
            house.co_id = co_id
            house.bu_id = bu_id
            house.ho_name = ho_name
            house.ho_floor = ho_floor
            house.ho_price = ho_price
            house.ho_build_size = ho_build_size
            house.ho_true_size = ho_true_size
            house.ho_share_size = ho_share_size
            house.ho_room_type = ho_room_type
            house.insert_db()
        except Exception as e:
            print('co_index={}, 房号错误，url={}'.format(self.co_index, house_url), e)
