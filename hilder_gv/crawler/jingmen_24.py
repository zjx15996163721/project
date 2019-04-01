"""
url = http://www.jmfc.com.cn/index/caid-2/addno-1/page-1.html
city : 荆门
CO_INDEX : 24
小区数量：345
"""
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl
import requests, re

url = 'http://www.jmfc.com.cn/index/caid-2/addno-1/page-1.html'
co_index = '24'
city = '荆门'


class Jingmen(object):
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
                       page_count_rule='>>></a>.*?href=".*?page-(.*?)\.html',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_url = 'http://www.jmfc.com.cn/index/caid-2/addno-1/page-' + str(i) + '.html'
            p = ProducerListUrl(page_url=all_url,
                                request_type='get', encode='gbk',
                                analyzer_rules_dict=None,
                                current_url_rule="/html/body/div[5]/div[6]/div/div[2]/h3/a/@href",
                                analyzer_type='xpath',
                                headers=self.headers)
            comm_url_list = p.get_current_page_url()
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm.co_id = '楼盘首页.*?aid-(.*?)/'
                comm.co_name = 'class="ls">(.*?)<'
                comm.co_type = '物业类型</em>(.*?)<'
                comm.area = '区域所属：</em>(.*?)<'
                comm.co_green = '绿 化 率：</em>(.*?)<'
                comm.co_volumetric = '容 积 率：</em>(.*?)<'
                comm.co_build_type = '楼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;层：</em>(.*?)<'
                comm.co_size = '占地面积：</em>(.*?)<'
                comm.co_build_size = '建筑面积：</em>(.*?)<'
                comm.co_develops = '开&nbsp;&nbsp;发&nbsp;&nbsp;商：</em><.*?target="_blank">(.*?)<'
                comm.co_address = '项目地址：</em>(.*?)<'
                data_list = comm.to_dict()
                p = ProducerListUrl(page_url=i,
                                    request_type='get', encode='gbk',
                                    analyzer_rules_dict=data_list,
                                    current_url_rule='colspan="3" align="right"><a href="(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                more_build_url = p.get_details()
                self.get_build_info(more_build_url)
            except Exception as e:
                print(e)

    def get_build_info(self, more_build_url):
        for i in more_build_url:
            try:
                build = Building(co_index)
                build_url = 'http://www.jmfc.com.cn/' + i
                build.bu_num = '<tr bgcolor="#FFFFFF">.*?<td.*?>(.*?)<'
                build.co_id = '楼盘首页.*?aid-(.*?)/'
                build.bu_id = '&addno=12&action=loupantable&lzbm=(.*?)&ql_xh='
                build.bu_pre_sale = '<tr bgcolor="#FFFFFF">.*?<td.*?>.*?<.*?<td.*?>(.*?)<'
                build.bu_floor = '<tr bgcolor="#FFFFFF">.*?<td.*?>.*?<.*?<td.*?>.*?<.*?<td.*?>(.*?)<'
                build.bu_all_house = '<tr bgcolor="#FFFFFF">.*?<td.*?>.*?<.*?<td.*?>.*?<.*?<td.*?>.*?<.*?<td.*?>(.*?)<'
                p = ProducerListUrl(page_url=build_url,
                                    request_type='get', encode='gbk',
                                    analyzer_rules_dict=build.to_dict(),
                                    current_url_rule='<tr bgcolor="#FFFFFF">.*?align="left".*?href="(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                house_url_list = p.get_details()
                self.get_house_info(house_url_list)
            except Exception as e:
                print(e)

    def get_house_info(self, house_url_list):
        for i in house_url_list:
            try:
                build_url = 'http://www.jmfc.com.cn' + i
                response = requests.get(build_url, headers=self.headers)
                html = response.text
                bu_id = re.search('lzbm=(.*?)&', build_url).group(1)
                ho_name_list = re.findall('width="35%".*?房号:.*?<TD.*?>(.*?)<', html, re.S | re.M)
                ho_true_size_list = re.findall('width="35%".*?房号:.*?<TD.*?<TD.*?<TD.*?>(.*?)<', html, re.S | re.M)
                ho_type_list = re.findall('width="35%".*?房号:.*?<font.*?<TD.*?<TD.*?>(.*?)<', html, re.S | re.M)
                for i in range(0, len(ho_name_list)):
                    try:
                        house = House(co_index)
                        house.ho_name = ho_name_list[i].strip()
                        house.ho_true_size = ho_true_size_list[i].strip()
                        house.ho_type = ho_type_list[i].strip()
                        house.bu_id = bu_id
                        house.insert_db()
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
