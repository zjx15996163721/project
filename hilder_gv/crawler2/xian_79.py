"""
url = http://www.fang99.com/fcywbllc/yszcx.aspx
city : 西安
CO_INDEX : 79
小区数量：
"""
import re
import requests
from backup.comm_info import Comm, Building, House

url = 'http://www.fang99.com/fcywbllc/yszcx.aspx'
co_index = '79'
city = '西安'


class Xian(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def request_proxy(self, url, headers):
        data = {"app_name": 'gv_xian'}
        while True:
            ip = requests.post(url='http://192.168.0.235:8999/get_one_proxy', data=data).text
            print(ip)
            proxy = {
                'http': ip
            }
            try:
                res = requests.get(url=url, headers=headers, proxies=proxy, timeout=10)
                print(res.status_code)
                if res.status_code == 200:
                    print(ip, 'can use')
                    return res
            except Exception as e:
                form_data = {"app_name": 'gv_xian', "status_code": 1, "ip": ip}
                requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=form_data)
                print('ip有问题')

    def start_crawler(self):
        res = self.request_proxy(url, headers=self.headers)
        html_page = res.text
        page = re.search('\.\.\..*?page=(.*?)"', html_page, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            all_page_url = 'http://www.fang99.com/fcywbllc/yszcx.aspx?page=' + str(i)
            try:
                response = self.request_proxy(all_page_url, headers=self.headers)
                html = response.content.decode('gbk')
                comm_url_list = re.findall("fwzx_table_border.*?href='(.*?)'", html, re.S | re.M)
                for comm_url in comm_url_list:
                    try:
                        self.get_comm_info(comm_url)
                    except Exception as e:
                        print('小区错误，co_index={},url='.format(co_index, comm_url), e)
            except Exception as e:
                print('page页错误，co_index={},url={}'.format(co_index, all_page_url), e)

    def get_comm_info(self, comm_url):
        comm = Comm(co_index)
        comm_url = comm_url.replace('buildingdetail', 'buildinfo')
        response = self.request_proxy(comm_url, headers=self.headers)
        html = response.content.decode('gbk')
        comm.co_name = re.search('class="sf_xq_xmmc">(.*?)<', html, re.S | re.M).group(1).strip()
        comm.area = re.search('id="Label_CityArea">(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_pre_sale_date = re.search('class="sf_xq_jfsj">(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_build_type = re.search('id="lbl_JZJG".*?>(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_address = re.search('id="Label_ProjectAdress">(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_pre_sale = re.search('id="Label_SallPreDocuments">(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_all_house = re.search('id="lbl_ZTS".*?>(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_build_size = re.search('id="lbl_JZMJ".*?>(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_all_size = re.search('id="lbl_ZDMJ".*?>(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_develops = re.search('id="Label_DevName">.*?>(.*?)<', html, re.S | re.M).group(1).strip()
        comm.co_id = re.search('action=.*?buildingid=(.*?)"', html, re.S | re.M).group(1).strip()
        comm.insert_db()
        buildingid = re.search('buildingid=(.*?)$', comm_url, re.S | re.M).group(1)
        self.get_build_info(buildingid, comm.co_id)

    def get_build_info(self, buildingid, co_id):
        build_url = 'http://b.fang99.com/buildinglistselect.aspx?buildingid=' + buildingid
        response = self.request_proxy(build_url, headers=self.headers)
        html = response.content.decode('gbk')
        build_html = re.search('<div id="lzlist".*?</div>', html, re.S | re.M).group()
        build_info_list = re.findall('<td.*?</td>', build_html, re.S | re.M)
        for i in build_info_list:
            try:
                build = Building(co_index)
                build.bu_id = re.search("id='(.*?)'", i, re.S | re.M).group(1)
                build.bu_num = re.search("<a.*?>(.*?)<", i, re.S | re.M).group(1)
                build.co_id = co_id
                build.insert_db()
                self.get_house_info(build.bu_id, co_id)
            except Exception as e:
                print('楼栋错误，co_index={},url='.format(co_index, build_url), e)

    def get_house_info(self, bu_id, co_id):
        house_url = 'http://b.fang99.com/buildinglistselect.aspx?buildingid=' + co_id + '&xmbh=&lzbh=' + bu_id
        response = self.request_proxy(house_url, headers=self.headers)
        html = response.content.decode('gbk')
        house_html = re.search('rpt_ewlpblc_fjlistdiv_0.*?erp_con_2', html, re.S | re.M).group()
        house_info_list = re.findall('<span.*?</span>', house_html, re.S | re.M)
        for i in house_info_list:
            try:
                house = House(co_index)
                house.ho_room_type = re.search('title="(.*?),', i, re.S | re.M).group(1)
                house.ho_build_size = re.search('title=".*?,(.*?)"', i, re.S | re.M).group(1)
                if '<a' in i:
                    house.ho_name = re.search('<a.*?>(.*?)<', i, re.S | re.M).group(1)
                else:
                    house.ho_name = re.search('<span.*?>(.*?)<', i, re.S | re.M).group(1)
                house.bu_id = bu_id
                house.co_id = co_id
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_url), e)
