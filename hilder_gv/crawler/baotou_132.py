"""
数据太乱，没有用
"""

"""
url = http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init
city : 包头
CO_INDEX : 132
小区数量：
"""

import requests
from backup.comm_info import Comm
from backup.get_page_num import AllListUrl
import re

url = 'http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init'
co_index = '132'
city = '包头'


class Cangzhou(object):
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
                       page_count_rule='> ..<a.*?>(.*?)<',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            page_url = "http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init&page=" + str(i)
            response = requests.get(page_url, headers=self.headers)
            html = response.text
            comm_url_list = re.findall(
                'href="(http://zfbzj.baotou\.gov\.cn/index\.php\?m=content&c=permit&a=show&id=.*?)".*?http://zfbzj',
                html, re.S | re.M)
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm = Comm(co_index)
            response = requests.get(comm_url, headers=self.headers)
            html = response.text
            comm.co_pre_sale = re.search('预销售许可证号.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_develops = re.search('开发建设单位.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_handed_time = re.search('发证日期.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_name = re.search('项 目 名 称.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_address = re.search('项 目 座 落.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
