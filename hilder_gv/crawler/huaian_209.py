"""
url = http://222.184.103.50:7700/index.aspx
city : 淮安
CO_INDEX : 209
小区数量：
对应关系：
"""
import requests
from backup.comm_info import Comm, Building, House
import re

url = 'http://222.184.103.50:7700/index.aspx'
co_index = '209'
city = '淮安'
count = 0


class Huaian(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.area_url_list = [
            ('清河区', '223001'),
            ('青浦区', '223002'),
            ('经济开发区', '223005'),
            ('淮阴区', '223300'),
            ('淮安区', '223200'),
            ('金湖区', '211600'),
            ('涟水县', '223400'),
            ('盱眙县', '211700'),
            ('洪泽县', '223100'),
        ]

    def start_crawler(self):
        for area, code in self.area_url_list:
            html_list = []
            all_html_list = self.recur_page(code, html_list)
            self.get_comm_info(all_html_list)

    def recur_page(self, code, html_list):
        area_url = 'http://222.184.103.50:7700/WW/GQXProject.aspx?county=' + code
        response = requests.get(area_url, headers=self.headers)
        html = response.text
        html_list.append(html)
        while True:
            if 'id="lnkbtnNext" disabled="disabled"' not in html:
                formdata = self.get_view_state(html, code)
                res = requests.post(area_url, headers=self.headers, data=formdata)
                html = res.text
                html_list.append(html)
            else:
                break
        return html_list

    def get_comm_info(self, all_html_list):
        for html in all_html_list:
            try:
                comm_info_paper_list = re.findall('<tr>.*?</tr>', html, re.S | re.M)
                for i in comm_info_paper_list[1:]:
                    comm = Comm(co_index)
                    comm.area = re.search('align="center">(.*?)<', i, re.S | re.M).group(1)
                    comm.co_name = re.search('align="center".*?align="center".*?>(.*?)<', i, re.S | re.M).group(1)
                    comm.co_address = re.search('align="center".*?align="center".*?align="center".*?title="(.*?)"', i,
                                                re.S | re.M).group(1)
                    comm.co_all_house = re.search(
                        'align="center".*?align="center".*?align="center".*?align="center".*?>(.*?)<',
                        i, re.S | re.M).group(1)
                    comm.co_id = re.search('projectID=(.*?)&', i, re.S | re.M).group(1)
                    comm.insert_db()
                    self.get_build_info(comm.co_id)
            except Exception as e:
                print('解析错误，co_index={},方法：get_comm_info'.format(co_index), e)

    def get_build_info(self, co_id):
        try:
            build_url = 'http://222.184.103.50:7700/WW/ZHList.aspx?projectID=' + co_id + '&projectname='
            response = requests.get(build_url, headers=self.headers)
            html = response.text
            build_info_list = re.findall('<tr bgcolor="#f5f5f5">.*?</tr>', html, re.S | re.M)
            for i in build_info_list:
                build = Building(co_index)
                build.bu_num = re.search('<a id="LH".*?>(.*?)<', i, re.S | re.M).group(1).strip()
                build.bu_all_house = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1).strip()
                build.bu_id = re.search('ZNo=(.*?)"', i, re.S | re.M).group(1).strip()
                build.co_id = co_id
                build.insert_db()
                self.get_house_url(build.bu_id, co_id)
        except Exception as e:
            print('请求错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_url(self, bu_id, co_id):
        try:
            house_url = 'http://222.184.103.50:7700/WW/houseMessage.aspx?projectID=' + co_id + '&ZNo=' + bu_id
            response = requests.get(house_url, headers=self.headers)
            html = response.text
            house_info = re.search('id="loupan".*?</form>', html, re.S | re.M).group()
            house_url_list = re.findall("onclick=.fb\('(.*?)'\)", house_info, re.S | re.M)
            self.get_house_detail(house_url_list, bu_id, co_id)
        except Exception as e:
            print('请求错误，co_index={},url={}'.format(co_index, house_url), e)

    def get_house_detail(self, house_url_list, bu_id, co_id):
        for i in house_url_list:
            try:
                house = House(co_index)
                house_detail_url = 'http://222.184.103.50:7700/WW/housedetail.aspx?houseID=' + i
                response = requests.get(house_detail_url, headers=self.headers)
                html = response.text
                house.ho_name = re.search('id="Label1">(.*?)<', html, re.S | re.M).group(1)
                house.ho_room_type = re.search('id="Label2">(.*?)<', html, re.S | re.M).group(1)
                house.ho_build_size = re.search('id="Label3">(.*?)<', html, re.S | re.M).group(1)
                house.co_id = co_id
                house.bu_id = bu_id
                house.insert_db()
            except Exception as e:
                print('请求错误，co_index={},url={}'.format(co_index, house_detail_url), e)

    def get_view_state(self, html, code):
        VIEWSTATE = re.search('id="__VIEWSTATE".*?value="(.*?)"', html, re.S | re.M).group(1)
        EVENTVALIDATION = re.search('id="__EVENTVALIDATION".*?value="(.*?)"', html, re.S | re.M).group(1)
        headers_ = {
            '__EVENTTARGET': 'lnkbtnNext',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': VIEWSTATE,
            'TextBox1': code,
            '__EVENTVALIDATION': EVENTVALIDATION
        }
        return headers_
