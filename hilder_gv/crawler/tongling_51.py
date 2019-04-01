"""
url = http://spf.tlfdc.cn/ShowBuild.asp
city : 铜陵
CO_INDEX : 51
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree

co_index = 51


class Tongling(Crawler):
    def __init__(self):
        self.start_url = "http://spf.tlfdc.cn/ShowBuild.asp"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def start_crawler(self):
        co = Comm(co_index)
        res = requests.get(self.start_url, headers=self.headers)
        con_html = etree.HTML(res.text)
        all_url_list = con_html.xpath("//table//tr//td[@width='150']/a/@href")
        for url in all_url_list:
            try:
                co_id = re.search('id=(\d+)', url).group(1)
                comm_url = "http://spf.tlfdc.cn/showprojectinfo.aspx?projectid=" + str(co_id)
                res = requests.get(comm_url, headers=self.headers)
                con = res.text
                co.co_id = co_id
                co.co_name = re.search('项目名称.*?name">(.*?)<', con, re.S | re.M).group(1)
                co.co_develops = re.search('开发商名称.*?_ch">(.*?)<', con, re.S | re.M).group(1)
                co.co_address = re.search('项目坐落.*?ss">(.*?)<', con, re.S | re.M).group(1)
                co.co_green = re.search('绿化率.*?Green">(.*?)<', con, re.S | re.M).group(1)
                co.co_size = re.search('土地面积.*?Area">(.*?)<', con, re.S | re.M).group(1)
                co.co_all_house = re.search('总套数.*?count">(.*?)<', con, re.S | re.M).group(1)
                co.co_volumetric = re.search('容积率.*?Area">(.*?)<', con, re.S | re.M).group(1)
                co.co_type = re.search('规划用途.*?use">(.*?)<', con, re.S | re.M).group(1)
                co.area = re.search('所在区县.*?name">(.*?)<', con, re.S | re.M).group(1)
                co.insert_db()
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)
                continue

            self.build_parse(co_id)

    def build_parse(self, co_id):
        bu = Building(co_index)

        url = "http://spf.tlfdc.cn/prjleft.aspx?projectid=" + str(co_id)
        res = requests.get(url, headers=self.headers)
        con_html = etree.HTML(res.text)
        build_url_list = con_html.xpath("//td[@colspan='2']/a/@href")[4:-1]
        a = con_html.xpath("//td[@width='54%']")

        for index in range(0, len(build_url_list)):
            try:
                build_info_url = "http://spf.tlfdc.cn/" + build_url_list[index]
                res = requests.get(build_info_url, headers=self.headers)
                con = res.text
                bu.co_id = co_id
                bu.bu_pre_sale_date = re.search('发证日期.*?Date">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_num = re.search('幢.*?did">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_pre_sale = re.search('编号.*?no">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_address = re.search('位置.*?ss">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_build_size = re.search('面积.*?Area">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_type = re.search('性质.*?type">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_all_house = re.search('套数.*?number">(.*?)<', con, re.S | re.M).group(1)
                bu.bu_id = re.search('id=(\d+)', build_url_list[index]).group(1)

                bu.insert_db()
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, build_info_url), e)
                continue
            try:
                house_url = a[index].xpath("./a/@href")[0]
                self.house_parse(house_url, co_id, bu.bu_id)
            except Exception as e:
                continue

    def house_parse(self, house_url, co_id, bu_id):
        ho = House(co_index)
        url = "http://spf.tlfdc.cn/" + house_url
        res = requests.get(url, headers=self.headers)
        con = res.text

        ho_name = re.findall('室号：(.*?)套', con, re.S | re.M)
        ho_room_type = re.findall('套型：(.*?)建', con, re.S | re.M)
        ho_build_size = re.findall('建筑面积：(.*?)参', con, re.S | re.M)
        ho_price = re.findall('价格：(.*?)元', con, re.S | re.M)
        ho_detail = re.findall('href="(show.*?\?id=\d+&id2=\d+&prjid=\d+)"', con, re.S | re.M)
        for index in range(0, len(ho_name)):
            try:
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = ho_name[index]
                ho.ho_room_type = ho_room_type[index]
                ho.ho_build_size = ho_build_size[index]
                ho.ho_price = ho_price[index]
                ho_detail_url = "http://spf.tlfdc.cn/" + ho_detail[index]
                res = requests.get(ho_detail_url, headers=self.headers)
                res = res.content.decode('gb2312')
                ho.ho_floor = re.findall('楼层.*?">(.*?)</td>', res, re.S | re.M)[0].strip()

                ho.insert_db()
            except:
                print('房号错误，co_index={},url={}'.format(co_index, url), e)
                continue
