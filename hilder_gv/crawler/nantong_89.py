"""
url = http://newhouse.ntfdc.net/house_certification.aspx
city : 南通
CO_INDEX : 89
小区数量：
"""

import requests
from backup.comm_info import Comm
import re

url = 'http://newhouse.ntfdc.net/house_certification.aspx'
co_index = '89'
city = '南通'


class Nantong(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def start_crawler(self):
        res = requests.get(url, headers=self.headers)
        content = res.text
        page = re.search('页数：1/(.*?) ', content, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            page_url = 'http://newhouse.ntfdc.net/house_certification.aspx?p=' + str(i)
            response = requests.get(page_url, headers=self.headers)
            html = response.text
            comm_html = re.search('class="layer-bd tb-style1">.*?</table>', html, re.S | re.M).group()
            comm_info_list = re.findall('<tr>.*?</tr>', comm_html, re.S | re.M)[1:]
            for info in comm_info_list:
                try:
                    comm = Comm(co_index)
                    comm.co_pre_sale = re.search('<td.*?>(.*?)<', info, re.S | re.M).group(1)
                    comm.co_name = re.search('<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                    comm.co_all_size = re.search('<td.*?<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                    comm.co_type = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                    comm.co_pre_sale_date = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', info,
                                                      re.S | re.M).group(
                        1)
                    comm.co_develops = re.search('<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', info,
                                                 re.S | re.M).group(
                        1)
                    comm.insert_db()
                except Exception as e:
                    print('小区错误，co_index={},url={}'.format(co_index, page_url), e)
