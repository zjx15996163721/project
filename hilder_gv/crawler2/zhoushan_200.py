"""
url = http://www.zstmsf.com/spf/dh.html?tb_key=
city :  舟山
CO_INDEX : 200
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
import random
from lib.log import LogHandler

co_index = '200'
city_name = '舟山'
log = LogHandler("zhoushan_200")

class Zhoushan(Crawler):
    def __init__(self):
        self.start_url = 'http://www.zstmsf.com/spf/'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.proxies = [{"http": "http://192.168.0.96:3234"},
                        {"http": "http://192.168.0.93:3234"},
                        {"http": "http://192.168.0.90:3234"},
                        {"http": "http://192.168.0.94:3234"},
                        {"http": "http://192.168.0.98:3234"},
                        {"http": "http://192.168.0.99:3234"},
                        {"http": "http://192.168.0.100:3234"},
                        {"http": "http://192.168.0.101:3234"},
                        {"http": "http://192.168.0.102:3234"},
                        {"http": "http://192.168.0.103:3234"}, ]
        self.region = {
            "dh":'定海','xc':'新城','ds':'岱山','ss':'嵊泗','pt':'普陀'
        }
    def start_crawler(self):
        for region in self.region.items():
            region_code = region[0]
            region_name = region[1]
            url = self.start_url + region_code + '.html'
            b = AllListUrl(first_page_url=url,
                           request_method='get',
                           analyzer_type='regex',
                           encode='utf-8',
                           page_count_rule='共(\d+)页>',
                           )
            page = b.get_page_count()
            for i in range(1,int(page)+1):
                new_url = url + "?page=" + str(i)
                res = requests.get(new_url,headers=self.headers)
                html = etree.HTML(res.text)
                co_list = html.xpath("//dl[@class='spf_lp_searchlist bg1']")
                for co in co_list:
                    comm = Comm(co_index)
                    co_url = co.xpath("./dt/h4/a/@href")[0]
                    comm.co_name = co.xpath("./dt/h4/a/text()")[0]
                    comm.co_address = co.xpath(".//address/text()")[0]
                    comm.co_id = re.search('\d+',co_url).group(0)
                    comm.co_develops = co.xpath("./dd[@class='dev']/a/text()")[0]
                    comm.co_plan_pro = co.xpath("./dt/h4/span/text()")[0]
                    comm.co_type = co.xpath(".//p/span[2]/text()")[0]
                    comm.area = region_name
                    comm.insert_db()

                    detail_url = "http://www.zstmsf.com" + co_url
                    self.bu_parse(detail_url,comm.co_id)

    def bu_parse(self,detail_url,co_id):
        pre_url = detail_url.replace('lp','presell')
        pre_res = requests.get(pre_url,headers=self.headers)
        pre_html = etree.HTML(pre_res.text)
        bu_pre_list = pre_html.xpath("//dt/strong/a")
        for bu_pre in bu_pre_list:
            bu_pre_url  = bu_pre.xpath("./@href")[0]
            bu_pre_sale = bu_pre.xpath("./text()")[0]
            bu_url  = 'http://www.zstmsf.com' + bu_pre_url
            while True:
                try:
                    proxy = self.proxies[random.randint(0,9)]
                    bu_res = requests.get(bu_url,headers=self.headers,proxies=proxy,timeout=10)
                    break
                except:
                    continue
            bu_html = etree.HTML(bu_res.text)
            bu_list = bu_html.xpath("//tr//strong/a/@href")
            for bo_url in bu_list:
                ho_url = "http://www.zstmsf.com" + bo_url
                while True:
                    try:
                        proxy = self.proxies[random.randint(0, 9)]
                        ho_res = requests.get(ho_url, headers=self.headers,proxies=proxy,timeout=10)
                        break
                    except:
                        continue
                build = Building(co_index)
                build.co_id = co_id
                build.bu_id = re.search('zid=.*?(\d+)',ho_url).group(1)
                build.bu_num = re.search('幢名称：<strong>(.*?)<',ho_res.text).group(1)
                build.bu_all_house = re.search("幢总套数.*?'>(.*?)</",ho_res.text).group(1)
                build.bu_all_size = re.findall("面积.*?'>(.*?)</",ho_res.text)[0]
                build.bu_pre_sale = bu_pre_sale
                build.insert_db()
                self.ho_parse(co_id,build.bu_id,ho_res)

    def ho_parse(self,co_id,bu_id,res):
        ho_html = etree.HTML(res.text)
        house_list = ho_html.xpath("//td[@title]")
        for house in house_list:
            house_info = house.xpath("./@title")[0]
            house_name = house.xpath(".//span/text()")[0]
            ho = House(co_index)
            ho.co_id =co_id
            ho.bu_id = bu_id
            ho.ho_name = house_name
            try:
                ho.ho_build_size = re.search('建筑面积:(.*?)\r',house_info).group(1)
                ho.ho_true_size =  re.search('套内面积:(.*?)\r',house_info).group(1)
                ho.ho_share_size =  re.search('分摊面积:(.*)',house_info).group(1)
            except Exception as e:
                log.info("房间无面积")
            ho.insert_db()





