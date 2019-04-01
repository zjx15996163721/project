"""
url = http://www.syfc.com.cn/work/xjlp/new_building.jsp
city :  沈阳
CO_INDEX : 45
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree

co_index = 45
count = 0
city = 'shenyang'


class Shenyang(Crawler):
    def __init__(self):
        self.start_url = "http://www.syfc.com.cn/work/xjlp/new_building.jsp"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def start_crawler(self):
        res = requests.get(self.start_url, headers=self.headers)
        con = res.text
        page = re.search('共(\d+)页', con).group(1)
        for i in range(1, int(page) + 1):
            url = self.start_url + "?page=" + str(i)
            try:
                res = requests.get(url, headers=self.headers)
            except Exception as e:
                print("co_index={},翻页问题".format(co_index),e)
                continue
            con_html = etree.HTML(res.text)
            html = con_html.xpath("//table[@bgcolor='#a4abb5']//tr")[1:-1]
            for tag in html:
                build_all_url, co_id = self.comm(tag)
                try:
                    res = requests.get(build_all_url,headers=self.headers)
                    self.build(res,co_id)
                except Exception as e:
                    print("co_index={},小区详情页无法访问".format(co_index),e)


    def comm(self, tag):
        co = Comm(co_index)
        co.co_name = tag.xpath("./td[@width='143']/a/text()")[0]
        co.area = tag.xpath("./td[@width='184']/text()")[0]
        co.co_develops = tag.xpath("./td[@width='192']/text()")[0]
        co_id = tag.xpath("./td/a/@href")[0]
        co.co_id = re.search('mmcid=(\d+)&', co_id).group(1)
        co.co_open_time = tag.xpath("./td[@width='95']/text()")[0]
        buid_all_url = "http://www.syfc.com.cn" + co_id
        co.insert_db()
        global count
        count += 1
        print(count)
        return buid_all_url, co.co_id

    def build(self, res, co_id):
        bu = Building(co_index)
        h = etree.HTML(res.text)
        bu_info = h.xpath("//table[@width='739']//td[@align='left']")
        for buil in bu_info:
            try:
                bu.co_id = co_id
                bu.bu_address = buil.xpath("./a/text()")[0]
                house_url = buil.xpath("./a/@href")[0]
                bu.bu_id = re.search('houseid=(\d+)&', house_url).group(1)

                bu.insert_db()
            except Exception as e:
                print("co_index={},楼栋信息错误".format(co_index),e)
                continue

            self.house(house_url, bu.bu_id, co_id)

    def house(self, house_url, bu_id, co_id):

        ho_url = "http://www.syfc.com.cn" + house_url
        try:
            res = requests.get(ho_url, headers=self.headers)
            con = etree.HTML(res.text)
            ho_detail_url = con.xpath("//iframe/@src")[0]
            response = requests.get(ho_detail_url, headers=self.headers)
        except Exception as e:
            print("co_index={},楼栋详情页无法访问".format(co_index),e)
        html = etree.HTML(response.text)
        content = html.xpath("//td[@width='70']")
        for td in content:
            ho = House(co_index)
            try:
                room_url = td.xpath("./a/@href")[0]
                ho.ho_name = td.xpath("./a/text()")[0]
                # ho.ho_id = re.search('id=(\d+)&', room_url).group(1)
                ho.bu_id = bu_id
                ho.co_id = co_id
                room_url = "http://www.syfc.com.cn" + room_url
                try:
                    res = requests.get(room_url, headers=self.headers)
                    con = res.text
                except Exception as e:
                    print("co_idnex={},房屋详情页无法访问".format(co_index),e)
                # print(con)
                ho.ho_build_size = re.search('建筑面积.*?">(.*?)<', con, re.S | re.M).group(1)
                ho.ho_share_size = re.search('分摊面积.*?">(.*?)<', con, re.S | re.M).group(1)
                ho.ho_true_size = re.search('套内面积.*?">(.*?)<', con, re.S | re.M).group(1)
                ho.ho_type = re.search('类型.*?">(.*?)<', con, re.S | re.M).group(1)
                ho.insert_db()
            except:
                ho.bu_id = bu_id
                ho.co_id = co_id
                ho.ho_name = td.xpath("./text()")[0]
                ho.insert_db()
