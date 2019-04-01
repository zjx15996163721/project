"""
url = http://123.131.127.13/xy/dzlist.asp
city : 潍坊
CO_INDEX : 95
小区数量：
"""
import requests
from backup.comm_info import Comm
from backup.get_page_num import AllListUrl
import time
import re

url = 'http://123.131.127.13/xy/dzlist.asp'
co_index = '95'
city = '潍坊'


class Weifang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='页次：<b><font color=red>1</font></b>/<b>(.*?)<',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            page_url = 'http://123.131.127.13/xy/dzlist.asp?page=' + str(i)
            time.sleep(5)
            response = requests.get(page_url, headers=self.headers)
            html = response.content.decode('gbk')
            comm_list_html = re.search('项目电子手册列表.*?<table(.*?)</table>', html, re.S | re.M).group(1)
            comm_html_list = re.findall('<tr>(.*?)</tr>', comm_list_html, re.S | re.M)[1:]
            self.get_comm_info(comm_html_list)

    def get_comm_info(self, comm_html_list):
        for i in comm_html_list:
            comm = Comm(co_index)
            comm.co_name = re.search('<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
            comm.co_develops = re.search('<td.*?><a.*?>(.*?)<', i, re.S | re.M).group(1)
            comm.co_address = re.search('<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
            detail_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
            self.get_comm_detail(detail_url, comm)

    def get_comm_detail(self, detail_url, comm):
        comm_url = 'http://123.131.127.13/xy/' + detail_url
        time.sleep(3)
        response = requests.get(comm_url, headers=self.headers)
        html = response.content.decode('gbk')
        comm.area = re.search('所属区县：.*?<td.*?>(.*?)<', html, re.S | re.M)
        if comm.area:
            comm.area = comm.area.group(1)
        else:
            comm.area = None
        comm.insert_db()
