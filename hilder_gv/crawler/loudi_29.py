"""
url = http://www.ldfdcw.com/newhouse/1.html
city : 娄底
CO_INDEX : 29
小区数量：254
"""
import requests
from lxml import etree
from backup.producer import ProducerListUrl
from backup.comm_info import Comm
from backup.get_page_num import AllListUrl

url = 'http://www.ldfdcw.com/index.php?caid=2&addno=1'
co_index = '29'
city = '娄底'


class Loudi(object):
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
                       page_count_rule='>>>.*?page=(.*?)"',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_page_url = url + '&page=' + str(i)
            response = requests.get(all_page_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            comm_url_list = tree.xpath('//div[@class="info"]/h3/a/@href')
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = i.replace('view', 'detail')
                comm.co_type = '物业类型：.*?<dd>(.*?)<'
                comm.area = '区域所属：.*?<dd>(.*?)<'
                comm.co_build_size = '建筑面积：.*?<dd>(.*?)<'
                comm.co_size = '占地面积：.*?<dd>(.*?)<'
                comm.co_green = '绿化率：.*?<dd><.*?>(.*?)<'
                comm.co_build_type = '楼　　层：.*?<dd>(.*?)<'
                comm.co_volumetric = '容积率：.*?<dd><.*?>(.*?)<'
                comm.co_id = '楼盘首页.*?newhouse/.*?/(.*?)/'
                comm.co_name = '<h1 class="title">(.*?)<'
                comm.co_address = '楼盘地址：.*?<dd>(.*?)<'
                comm.co_develops = '开发商：.*?<dd(.*?)<'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='gbk',
                                    analyzer_rules_dict=comm.to_dict(),
                                    analyzer_type='regex',
                                    headers=self.headers)
                p.get_details()
            except Exception as e:
                print(e)
