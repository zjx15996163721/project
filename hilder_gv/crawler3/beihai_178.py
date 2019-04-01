"""
url = http://www.beihaire.gov.cn/2j.asp?numberbj=13&id=145
city :  北海
CO_INDEX : 178
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '178'
city_name = '北海'
log = LogHandler('北海')

class Beihai(Crawler):
    def __init__(self):
        self.start_url = 'http://www.beihaire.gov.cn/2j.asp?numberbj=13&id=145'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        html = etree.HTML(res.content.decode('gbk'))
        page_str = html.xpath('//strong[1]/text()')[0]
        count = re.search('\d+',page_str).group(0)
        for i in range(1,int(count)+1):
            url = 'http://www.beihaire.gov.cn/2j.asp?numberbj=13&id=145&cid=0&page=' + str(i)
            page_res = requests.get(url,headers=self.headers)
            page_html = etree.HTML(page_res.content.decode('gbk'))
            tab_list = page_html.xpath("//td[@class='mframe-m-mid']/table")
            for tab in tab_list[2:-2]:
                try:
                    tmp_url = tab.xpath(".//td/a[2]/@href")[0]
                    numberbj = re.search('id=(\d+)&',tmp_url).group(1)
                    unid = re.search('unid=(\d+)',tmp_url).group(1)
                    pro_url = 'http://www.beihaire.gov.cn/news/list.asp?numberbj='+str(numberbj)+'&unid='+str(unid)
                    co_res = requests.get(pro_url,headers=self.headers)
                    co_html = etree.HTML(co_res.content.decode('gbk'))
                    co_list = co_html.xpath("//tr[@style]")
                except:
                    continue
                self.parse(co_list)
    def parse(self,co_list):
        for project in co_list[2:]:
            try:
                co = Comm(co_index)
                co.co_pre_sale_date = project.xpath("./td[1]/font/text()")[0]
                co.co_develops = project.xpath("./td[2]/font/text()")[0]
                co.co_pre_sale = project.xpath("./td[3]/font/text()")[0]
                co.co_name = project.xpath("./td[4]/font/text()")[0]
                co.co_address = project.xpath("./td[5]/font/text()")[0]
                co.co_use = project.xpath("./td[8]/font/text()")[0]
                try:
                    co.co_all_house = project.xpath("./td[11]/font/text()")[0]
                except:
                    log.info("无总套数")
                    co.co_all_house = None
                co.co_build_size = project.xpath("./td[10]/font/text()")[0]
                co.insert_db()
            except Exception as e:
                log.error("{}小区解析失败".format(project))
