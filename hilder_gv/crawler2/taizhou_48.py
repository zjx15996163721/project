"""
房号包找不到
"""
"""
url = http://tz.tmsf.com/newhouse/property_searchall.htm
city : 台州
CO_INDEX : 48
小区数量：639
"""

import re

import requests
from backup.comm_info import Comm, Building
from backup.get_page_num import AllListUrl

url = 'http://tz.tmsf.com/newhouse/property_searchall.htm'
co_index = '27'
city = '台州'


class Taizhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='green1">1/(.*?)<',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_url = 'http://tz.tmsf.com/newhouse/property_searchall.htm'
            data = {
                'keytype': 1,
                'page': page
            }
            response = requests.post(all_url, data=data, headers=self.headers)

            html = response.text
            comm_url_list = re.findall('<div class="build_txt">.*?<a href="(.*?)"', html, re.S | re.M)
            for i in comm_url_list:
                self.get_comm_detail(i)

    def get_comm_detail(self, comm_url):
        comm = Comm(co_index)
        co_url = 'http://tz.tmsf.com' + comm_url
        response = requests.get(co_url, headers=self.headers)
        html = response.content.decode('utf-8')
        comm.co_name = re.search('<span class="buidname colordg">(.*?)<', html, re.S | re.M).group(1)
        comm.co_address = re.search('楼盘地址：.*?<span.*?>(.*?)<', html, re.S | re.M).group(1)
        if '[' in comm.co_address:
            comm.area = re.search('\[(.*?)\]', comm.co_address, re.S | re.M).group(1)
        comm.co_type = re.search('物业类型：.*?<span title="(.*?)"', html, re.S | re.M).group(1)
        comm.co_open_time = re.search('最新开盘：</strong>(.*?)<', html, re.S | re.M).group(1)
        comm.co_develops = re.search('项目公司：</strong>(.*?)<', html, re.S | re.M).group(1)
        comm.co_build_type = re.search('建筑形式：</strong>(.*?)<', html, re.S | re.M).group(1)
        comm.co_id = re.search('id="propertyid".*?value="(.*?)"', html, re.S | re.M).group(1)
        comm.insert_db()
        sid = re.search('id="sid" name="sid" value="(.*?)"', html, re.S | re.M).group(1)
        build_url = re.search('id="index_bar">楼盘主页.*?href="(.*?)"', html, re.S | re.M).group(1)
        self.get_build_info(build_url, comm.co_id, sid)

    def get_build_info(self, build_url, co_id, sid):
        bu_url = 'http://tz.tmsf.com' + build_url
        response = requests.get(bu_url, headers=self.headers)
        html = response.content.decode('utf-8')
        build_info = re.search('幢　　号：.*?全部(.*?)</div>', html, re.S | re.M).group(1)
        build_list = re.findall('<a.*?</a>', build_info, re.S | re.M)
        for i in build_list:
            build = Building(co_index)
            build.bu_id = re.search("doBuilding\('(.*?)'\)", i, re.S | re.M).group(1)
            build.bu_num = re.search("<a.*?>(.*?)<", i, re.S | re.M).group(1)
            build.co_id = co_id
            build.insert_db()
            self.get_house_info(build.bu_id, sid, co_id)

    def get_house_info(self, bu_id, sid, co_id):
        house_url = 'http://tz.tmsf.com/newhouse/property_' + sid + '_' + co_id + '_price.htm?buildingid=' + bu_id + '&page=1'
        response = requests.get(house_url, headers=self.headers)
        html = response.content.decode('utf-8')
        page = re.search('页数 1/(\d+)	', html, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            ho_url = re.sub('page=\d+$', 'page={0}'.format(page), house_url)
            result = requests.get(ho_url, headers=self.headers).text
            ho_html = re.search('class="sjtd".*?一房一价列表end', result, re.S | re.M).group()
            ho_html_list = re.findall('<tr.*?</tr>', ho_html, re.S | re.M)
            for i in ho_html_list:
                h_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                self.get_house_detail(bu_id, co_id, h_url)

    def get_house_detail(self, bu_id, co_id, h_url):
        house_url = 'http://tz.tmsf.com/' + h_url
        response = requests.get(house_url, headers=self.headers)
        html = response.content.decode('utf-8')
        pass
