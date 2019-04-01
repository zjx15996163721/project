"""
url = http://www.f0795.cn/house/
city :  宜春
CO_INDEX : 64
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl
import re, requests
from lxml import etree

co_index = 64


class Yichun(Crawler):
    def __init__(self):
        self.start_url = "http://www.f0795.cn/house/"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='<cite>共.*?/(\d+)页',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            url = "http://www.f0795.cn/house/index-htm-page-" + str(i) + ".html"
            p = ProducerListUrl(page_url=url,
                                request_type='get', encode='utf-8',
                                analyzer_rules_dict=None,
                                current_url_rule="//ul[@class='list']//div[@class='text']/h3/a/@href",
                                analyzer_type='xpath',
                                headers=self.headers)
            comm_url_list = p.get_current_page_url()
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        co = Comm(co_index)
        for url in comm_url_list:
            comm_url = url + "xinxi.html"
            try:
                res = requests.get(comm_url, headers=self.headers)
                con = res.text
                html = etree.HTML(con)
                co.co_id = re.search('/(\d+)', con).group(1)
                co.co_name = html.xpath("//h1[@class='fl']/a/@title")[0]
                co.co_address = re.search("楼盘地址.*?>(.*?)</li>", con).group(1)
                co.co_all_house = re.search("规划户数.*?>(.*?)</li>", con).group(1)
                co.co_develops = re.search("开 发 商.*?>(.*?)</li>", con).group(1)
                co.area = re.search("片区.*?>(.*?)</li>", con).group(1)
                co.co_type = re.search("项目类型.*?>(.*?)</li>", con).group(1)
                co.co_build_type = re.search("建筑类型.*?>(.*?)</li>", con).group(1)
                co.co_size = re.search("规划面积.*?>(.*?)</li>", con).group(1)
                co.co_build_size = re.search("建筑面积.*?>(.*?)</li>", con).group(1)
                try:
                    co.co_open_time = re.search("开盘时间.*?>(.*?)</li>", con).group(1)
                except:
                    co.co_open_time = None
                co.co_green = re.search("绿 化 率.*?>(.*?)</li>", con).group(1)
                co.co_volumetric = re.search("容 积 率.*?>(.*?)</li>", con).group(1)
                try:
                    co.co_build_start_time = re.search("开工时间：(.*?)</span>", con).group(1)
                    co.co_build_end_time = re.search("竣工时间：(.*?)</span>", con).group(1)
                except:
                    co.co_build_start_time = None
                    co.co_build_end_time = None

                co.insert_db()
            except:
                continue
