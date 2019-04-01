"""
url = http://www.wzfg.com/realweb/stat/ProjectSellingList.jsp
city : 温州
CO_INDEX : 53
小区数量：
对应关系：
"""
import requests
from backup.comm_info import Comm, Building
import re

url = 'http://www.wzfg.com/realweb/stat/ProjectSellingList.jsp'
co_index = '53'
city = '温州'


class Wenzhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        for i in range(119):
            all_page_url = url + '?currPage=' + str(i)
            try:
                response = requests.get(all_page_url, headers=self.headers)
                html = response.text
                comm_url_list = re.findall("(FirstHandProjectInfo.*?)'", html, re.S | re.M)
                self.get_comm_info(comm_url_list)
            except Exception as e:
                print('page页错误，co_index={},url={},page={}'.format(co_index, all_page_url, i), e)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm_url = 'http://www.wzfg.com/realweb/stat/' + i
            try:
                comm = Comm(co_index)
                response = requests.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_develops = re.search('开发单位：.*?<a.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale = re.search('预售许可证号：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_pre_sale_date = re.search('发证日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.area = re.search('所在地区：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_build_size = re.search('>项目测算面积：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_name = re.search('项目名称：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_address = re.search('项目地址：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_open_time = re.search('开盘日期：.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_type = re.search('拟售价格（元/㎡）.*?center.*?center.*?>(.*?)<', html, re.S | re.M).group(1)
                comm.co_id = re.search('projectID=(.*?)$', comm_url).group(1)
                comm.insert_db()
                build_info_list = re.findall("floortitle' title='(.*?)'", html, re.S | re.M)
                bu_num_list = re.findall("floortitle.*?>(.*?)<", html, re.S | re.M)
                self.get_build_info(build_info_list, bu_num_list, comm.co_id, comm_url)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_info_list, bu_num_list, co_id, comm_url):
        for i in range(len(bu_num_list)):
            try:
                build = Building(co_index)
                build.co_id = co_id
                build.info = build_info_list[i]
                build.bu_num = bu_num_list[i]
                build.insert_db()
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, comm_url), e)
