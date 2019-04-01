"""
url = http://www.dzfgj.com/index.php?m=content&c=index&a=lists&catid=61
city : 达州
CO_INDEX : 146
小区数量：
"""

import requests
from backup.comm_info import Comm
from backup.get_page_num import AllListUrl
import re

url = 'http://www.dzfgj.com/index.php?m=content&c=index&a=lists&catid=61'
co_index = '146'
city = '达州'


class Dazhou(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='> ..<.*?>(.*?)<',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            page_all_url = 'http://www.dzfgj.com/index.php?m=content&c=index&a=lists&catid=61&page=' + str(i)
            response = requests.get(page_all_url, headers=self.headers)
            html = response.text
            comm_html = re.search('<tbody>.*?</tbody>', html, re.S | re.M).group()
            comm_info_list = re.findall('<tr>.*?</tr>', comm_html, re.S | re.M)
            self.get_comm_info(comm_info_list)

    def get_comm_info(self, comm_info_list):
        for i in comm_info_list:
            try:
                comm = Comm(co_index)
                comm.co_name = re.search('<td>(.*?)</td>', i, re.S | re.M).group(1)
                comm.co_all_house = re.search('<td.*?<td>(.*?)</td>', i, re.S | re.M).group(1)
                comm.co_all_size = re.search('<td.*?<td.*?<td>(.*?)</td>', i, re.S | re.M).group(1)
                comm.insert_db()
            except Exception as e:
                print('小区错误，co_index={},html_str={}'.format(co_index, i), e)
