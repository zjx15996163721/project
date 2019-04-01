"""
url = http://61.143.241.154/user_kfs.aspx
city :  韶关
CO_INDEX : 194
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '194'
city_name = '韶关'
log = LogHandler('韶关')

class Shaoguan(Crawler):
    def __init__(self):
        self.start_url = 'http://61.143.241.154/user_kfs.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer':
                'http://61.143.241.154/user_itemlist.aspx'
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

    def start_crawler(self):
        count = 1
        while True:
            url = "http://61.143.241.154/user_itemlist.aspx?page=" + str(count)
            res = requests.get(url,headers=self.headers)
            res.encoding = 'gbk'
            if '找不到相关信息' in res.text:
                break
            html = etree.HTML(res.text)
            url_list = html.xpath("//table[@id='listtable']/tr")
            for com_info in url_list[1:]:
                co_name = com_info.xpath("./td/a/text()")[0]
                co_addr = com_info.xpath("./td[2]/text()")[0]
                co_area = com_info.xpath("./td[3]/text()")[0]
                com_url = com_info.xpath("./td/a/@href")[0]
                if '9090' in com_url:
                    co_url = com_url
                else:
                    co_url = 'http://61.143.241.154/' + com_url
                self.comm_parse(co_name,co_addr,co_area,co_url)
            count += 1

    def comm_parse(self,co_name,co_addr,co_area,co_url):
        co_res = requests.get(co_url,headers=self.headers)
        co_res.encoding = 'gbk'
        con = co_res.text
        co = Comm(co_index)
        if re.search('开发商名称.*?;">(.*?)</',con,re.S|re.M):
            co.co_develops = re.search('开发商名称.*?;">(.*?)</',con,re.S|re.M).group(1)
        else:
            co.co_develops = None

        kfsid = re.search('kfsid=(\d+)',co_url).group(1)
        co.co_id = co_name+kfsid
        co.co_name = co_name
        co.co_address = co_addr
        co.area = co_area
        co.co_all_house = re.search('总套数.*?">(\d+)&nbsp',con,re.S|re.M).group(1)
        co.co_all_size = re.search('总面积.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
        co.co_residential_size = re.search('住宅面积.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
        co.insert_db()
        num = 1
        while True:
            pre_url = co_url + "&ypage=" + str(num)    # 预售翻页
            pre_res = requests.get(pre_url,headers=self.headers)
            pre_con = pre_res.content.decode('gbk')
            pre_html = etree.HTML(pre_con)
            if pre_html.xpath("//table[@id='preselltable1']//tr[@bgcolor='white']"):
                pre_list = pre_html.xpath("//table[@id='preselltable1']//tr[@bgcolor='white']")
                num += 1
                for pre in pre_list:
                    bu_url = pre.xpath("./td[4]/a/@href")[0]
                    if 'user_Presell' in bu_url:
                        self.bu_parse(bu_url,co.co_id,co_url)
                    else:
                        continue
            else:
                break

        while True:
            sell_url = co_url + "&page=" + str(num)    # 现售翻页
            sell_res = requests.get(sell_url, headers=self.headers)
            sell_con = sell_res.content.decode('gbk')
            sell_html = etree.HTML(sell_con)
            if sell_html.xpath("//table[@id='selltable1']//tr[@bgcolor='white']"):
                sell_list = sell_html.xpath("//table[@id='selltable1']//tr[@bgcolor='white']")
                num += 1
                for sell in sell_list:
                    ho_url = sell.xpath("./td/a/@href")[0]
                    if 'user_sell' in ho_url:
                        bu_id = re.search('ID=(.*?)&',ho_url).group(1)
                        self.house_parse(ho_url,co.co_id,bu_id)
                    else:
                        continue
            else:
                break


    def bu_parse(self,bu_url,co_id,co_url):
        build_url = "http://61.143.241.154/" + bu_url
        global headers
        headers =  {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer':
                co_url
        }
        bu_res = requests.get(build_url,headers=headers)
        bu_con = bu_res.content.decode('gbk')
        bu_pre_sale = re.search('预售许可证编号.*?blank">(.*?)</a',bu_con,re.S|re.M).group(1)
        bu_pre_sale_date = re.search('预售证有效日期.*?">(.*?)</td',bu_con,re.S|re.M).group(1)
        bu_html = etree.HTML(bu_con)
        bu_list = bu_html.xpath("//table[@id='donglist']//tr")
        for bo in bu_list:
            bu = Building(co_index)
            bu.co_id = co_id
            bo_url = bo.xpath("./td/a/@href")[0]
            bu.bu_id = re.search('dbh=(.*?)&', bo_url).group(1)
            bu.bu_num = bo.xpath("./td[3]/text()")[0]
            bu.bu_floor = bo.xpath("./td[4]/text()")[0]
            bu.bu_pre_sale = bu_pre_sale
            bu.bu_pre_sale_date = bu_pre_sale_date
            bu.insert_db()
            self.house_parse(bo_url,co_id,bu.bu_id)

    def house_parse(self,ho_url,co_id,bu_id):
        house_url = "http://61.143.241.154/" + ho_url
        ho_res = requests.get(house_url,headers=headers)
        html = etree.HTML(ho_res.content.decode('gbk'))
        detail_list = html.xpath("//td[@height='80']/a/@href")
        for detail in detail_list:
            try:
                detail_url = 'http://61.143.241.154/'+detail
                res = requests.get(detail_url,headers=headers)
                con = res.content.decode('gbk')
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = re.search('房屋号.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.ho_true_size = re.search('套内面积.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.ho_build_size = re.search('建筑面积.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.orientation = re.search('房屋朝向.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.ho_type = re.search('用途.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.ho_price = re.search('申报总价.*?">(.*?)</td',con,re.S|re.M).group(1)
                ho.insert_db()
            except Exception as e:
                log.error("{}房屋请求解析失败{}".format(detail,e))














