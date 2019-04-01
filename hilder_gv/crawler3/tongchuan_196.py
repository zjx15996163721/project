"""
url = 'http://zjj.tongchuan.gov.cn/yw_list.action?c=137'
city :  铜川
CO_INDEX : 196
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm
import re, requests
from lib.log import LogHandler
from lxml import etree

co_index = '196'
city_name = '铜川'
log = LogHandler('铜川')

class Tongchuan(Crawler):
    def __init__(self):
        self.start_url = 'http://zjj.tongchuan.gov.cn/yw_list.action?c=137'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        page = re.search('(\d+)/\d+页',res.content.decode()).group(1)
        for i in range(1,int(page)+1):
            url = 'http://zjj.tongchuan.gov.cn/yw_list.action?c=137&pageNum='+str(i)
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content.decode())
            self.parse(html)

    def parse(self,html):
            co_list = html.xpath("//table[@cellspacing='1']//tr")
            for i in co_list[1:-2]:
                co = Comm(co_index)
                detail_url = i.xpath("./td/a/@href")[0]
                co.co_id = re.search('id=(.*?)&',detail_url).group(1)
                co.co_name = i.xpath("./td[1]/text()")[0]
                co.co_pre_sale = i.xpath("./td[2]/text()")[0]
                co.co_pre_sale_date = i.xpath("./td[3]/text()")[0]
                co.co_address = i.xpath("./td[4]/text()")[0]
                co.co_develops = i.xpath("./td[5]/text()")[0]
                co.insert_db()


