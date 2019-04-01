"""
url = http://218.28.223.13/zzzfdc/zhengzhou/permission.jsp
city :  郑州
CO_INDEX : 174
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm
import re, requests
from lxml import etree
from lib.log import LogHandler
import math

co_index = '174'
city_name = '郑州'
log = LogHandler('郑州')
class Zhengzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://218.28.223.13/zzzfdc/zhengzhou/permission.jsp'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        content = res.content.decode()
        count = re.search('共(\d+)条记录',content).group(1)
        page = math.ceil(int(count)/15)
        for i in range(1,int(page)+1):
            url = "http://218.28.223.13/zzzfdc/zhengzhou/permission.jsp?pn=&cn=&it=&pager.offset=15&page="+str(i)
            page_res = requests.get(url,headers=self.headers)
            html = etree.HTML(page_res.content.decode())
            project_list = html.xpath("//table//td/a/@href")
            for project in project_list:
                try:
                    project_url = 'http://218.28.223.13'+project
                    co_res = requests.get(project_url,headers=self.headers)
                    con = co_res.content.decode()
                    co_html = etree.HTML(con)
                    co = Comm(co_index)
                    co.co_id = re.search('number=(.*)',project).group(1)
                    co.co_name = re.search('LpName=(.*?)"',con,re.S|re.M).group(1)
                    co.co_pre_sale = re.search('预售许可证号.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_pre_sale_date = re.search('发证日期.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_develops = re.search('开发建设单位.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_address = re.search('项 目 坐 落.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_build_start_time = re.search('竣工时间.*?">(.*?)-----',con,re.S|re.M).group(1)
                    co.co_build_end_time = re.search('-----(.*?)</td',con,re.S|re.M).group(1)
                    co.co_build_size = co_html.xpath("//tr[9]/td[1]/text()")[0]
                    co.co_plan_pro = co_html.xpath("//tr[13]/td[4]/text()")[0]
                    co.co_land_use = co_html.xpath("//tr[13]/td[3]/text()")[0]
                    co.co_work_pro = co_html.xpath("//tr[13]/td[5]/text()")[0]
                    co.insert_db()
                except:
                    log.error("{}小区解析失败".format(project_url))
