"""
url = http://113.106.199.148/web/presale.jsp?page=2
city : 惠州
CO_INDEX : 21
author: 吕三利
小区数量：401
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from backup.tool import Tool

url = 'http://113.106.199.148/web/presale.jsp?page=1'
co_index = '21'
city = '惠州'


class Huizhou(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='第1页 / 共(.*?)页',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_url = 'http://113.106.199.148/web/presale.jsp?page=' + str(i)
            try:
                self.get_comm_url(all_url)
            except Exception as e:
                print('page页错误，co_index={},url={}'.format(co_index, all_url), e)

    def get_house_info(self, house_url, bu_id, co_id):
        try:
            house = House(co_index)
            house.bu_id = bu_id
            house.co_id = co_id
            response = requests.post(house_url, headers=self.headers)
            html = response.content.decode('gbk')
            house.ho_floor = re.search('所在楼层：.*?<td>(.*?)<', html, re.M | re.S).group(1)
            house.ho_name = re.search('房号：.*?<td>(.*?)<', html, re.M | re.S).group(1)
            house.ho_build_size = re.search('预测总面积：.*?<td>(.*?)<', html, re.M | re.S).group(1)
            house.ho_true_size = re.search('预测套内面积.*?<td>(.*?)<', html, re.M | re.S).group(1)
            house.ho_share_size = re.search('预测公摊面积.*?<td>(.*?)<', html, re.M | re.S).group(1)
            house.insert_db()
        except Exception as e:
            print('房号错误，co_index={},url={}'.format(co_index, house_url), e)

    def get_build_info(self, build_url, bu_id, co_id):
        bu_url = 'http://113.106.199.148/web/' + build_url
        resposne = requests.get(bu_url, headers=self.headers)
        html = resposne.text
        house_url_list = re.findall("onclick=' openContent\((.*?)\)", html, re.S | re.M)
        for i in house_url_list:
            code = i.split(',')
            house_url = "http://113.106.199.148/web/House.jsp?id=" + code[0] + "&lcStr=" + code[1]
            self.get_house_info(house_url, bu_id, co_id)

    def get_comm_detail(self, comm_detail_url):
        comm = Comm(co_index)
        try:
            response = requests.get(comm_detail_url, headers=self.headers)
            html = response.text
            comm.co_pre_sale = re.search('预售许可证号：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_land_use = re.search('土地使用权证号及用途：.*?<td.*?>(.*?)</td', html, re.S | re.M).group(1)
            comm.co_build_size = re.search('本期预售总建筑面积：.*?<td.*?>(.*?)</td', html, re.S | re.M).group(1)
            comm.co_all_house = re.search('本期总单元套数：.*?<td.*?>(.*?)</td', html, re.S | re.M).group(1)
            comm.co_pre_sale_date = re.search('发证日期：.*?<td.*?>(.*?)</td', html, re.S | re.M).group(1)
            return comm
        except Exception as e:
            print('小区详情错误，co_index={},url={}'.format(co_index, comm_detail_url), e)
            return comm

    def get_comm_url(self, all_url):
        response = requests.get(all_url, headers=self.headers)
        html = response.text
        comm_html = re.search('项目地址<.*?</table>', html, re.S | re.M).group()
        comm_info_list = re.findall('<tr>(.*?)</tr>', comm_html, re.S | re.M)
        for i in comm_info_list:
            comm_detail = re.search('href="(.*?)"', i, re.S | re.M).group(1)
            tool = Tool()
            replace_str = tool.url_quote(comm_detail, encode='gbk')
            comm_detail_url = 'http://113.106.199.148/web/' + replace_str
            comm = self.get_comm_detail(comm_detail_url)
            comm_url_encode = re.search('href=.*?href="(.*?)"', i, re.S | re.M).group(1)
            replace_str = tool.url_quote(comm_url_encode, encode='gbk')
            comm_url = 'http://113.106.199.148/web/' + replace_str
            self.get_comm_info(comm_url,comm)

    def get_comm_info(self, comm_url,comm):
        try:
            response = requests.get(comm_url, headers=self.headers)
            html = response.text
            comm.co_id = re.search('jectcode=(.*?)"', html, re.S | re.M).group(1)
            comm.co_name = re.search("项目名称：.*?<td.*?>(.*?)<", html, re.S | re.M).group(1)
            comm.co_address = re.search('项目地址：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_develops = re.search('开发企业：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_owner = re.search('国土证书：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.area = re.search('行政区划：</th>.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.insert_db()
            build_html = re.search('套房信息.*?</table>', html, re.S | re.M).group()
            build_info_list = re.findall('<tr.*?>.*?</tr>', build_html, re.S | re.M)
            for i in build_info_list:
                try:
                    build = Building(co_index)
                    build.co_id = comm.co_id
                    build.bu_num = re.search('<td.*?>(.*?)</td', i, re.S | re.M).group(1)
                    build.bu_id = re.search('buildingcode=(.*?)&', i, re.S | re.M).group(1)
                    build.co_build_structural = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_all_house = re.search('<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_floor = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.insert_db()
                    house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                    self.get_build_info(house_url, build.bu_id, comm.co_id)
                except Exception as e:
                    print('楼栋错误，co_index={},url={}'.format(co_index, comm_url), e)
        except Exception as e:
            print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)
