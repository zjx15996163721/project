"""
url = http://www.hbsfdc.com/Templets/HuaiBei/aspx/spflist.aspx
city :  淮北
CO_INDEX : 182
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from urllib import parse
from lxml import etree
from lib.log import LogHandler

co_index = '182'
city_name = '淮北'
log = LogHandler('jilin')

class Huaibei(Crawler):
    def __init__(self):

        self.start_url = 'http://www.hbsfdc.com/Templets/HuaiBei/aspx/spflist.aspx'
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

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='共.*?Count">(\d+)</span>页',
                       )
        page = b.get_page_count()
        data = {'__EVENTTARGET':'navigate$LnkBtnGoto'}
        for i in range(1,int(page)+1):
            if i == 1:
                res = requests.get(self.start_url,headers=self.headers)
                con = res.content.decode()
                html = etree.HTML(con)
                view_state = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
                valid = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
                data['__VIEWSTATE'] = view_state
                data['__EVENTVALIDATION'] = valid
                self.comm_list(html)
            else:
                data['navigate$txtNewPageIndex'] = i
                res = requests.post(self.start_url,data=data,headers=self.headers)
                con = res.content.decode()
                html = etree.HTML(con)
                view_state = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
                valid = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
                data['__VIEWSTATE'] = view_state
                data['__EVENTVALIDATION'] = valid
                self.comm_list(html)

    def comm_list(self,html):
        com_list = html.xpath("//table[@id='data_table_2']//tr/td[3]/a/@href")
        for com_temp in com_list:
            com_url = 'http://www.hbsfdc.com'+com_temp.replace("../../..",'')
            try:
                com_res = requests.get(com_url,headers=self.headers)
            except Exception as e:
                log.error("{}小区访问失败".format(com_url))
                continue
            com_con = com_res.content.decode()
            co = Comm(co_index)
            co.co_id = re.search('lcode=(\d+)',com_temp).group(1)
            co.co_name = re.search('项目名称.*?XMMC">(.*?)</span',com_con,re.S|re.M).group(1)
            co.co_develops = re.search('开发公司.*?NAME">(.*?)</span',com_con,re.S|re.M).group(1)
            co.co_address = re.search('项目地址.*?XMDZ">(.*?)</span',com_con,re.S|re.M).group(1)
            co.area = re.search('所在区域.*?SZQY">(.*?)</span',com_con,re.S|re.M).group(1)
            co.co_volumetric = re.search('容积率.*?RJL">(.*?)</span',com_con,re.S|re.M).group(1)
            co.co_pre_sale = re.search('预售证号.*?ZH">(.*?)</span',com_con,re.S|re.M).group(1)
            co.co_build_size = re.search('总建筑面积.*?JZMJ">(.*?)</span',com_con,re.S|re.M).group(1)
            co.insert_db()
            bu_list = re.findall("input name='radiobuild'.*?</td>",com_con)
            for bu in bu_list:
                bid = re.search('bid=(\d+)',bu).group(1)
                bo = Building(co_index)
                bo.co_id = co.co_id
                bo.bu_id = bid
                bo.bu_num = re.search('/>(.*?)</td>',bu).group(1)
                bo.insert_db()
                self.ho_parse(bid,co.co_id)

    def ho_parse(self,bid,co_id):

        payload = '<?xml version="1.0" encoding="utf-8" standalone="yes"?><param funname="SouthDigital.CMS.CBuildTableEx.GetBuildHTMLEx"><item>'\
              +bid+'</item><item>1</item><item>1</item><item>100</item><item>1000</item><item>g_oBuildTable</item><item> 1=1</item><item>1</item></param>'
        payload = parse.quote(payload)
        try:
            res = requests.post('http://www.hbsfdc.com/Common/Agents/ExeFunCommon.aspx',data=payload,headers=self.headers)
        except Exception as e:
            log.error("{}楼栋请求失败".format(bid))
        con = res.content.decode()
        ho_list = re.findall("title='(.*?)'>",con,re.S|re.M)
        for ho in ho_list:
            house = House(co_index)
            house.co_id = co_id
            house.bu_id = bid
            house.ho_name = re.search('房号：(.*)',ho).group(1)
            house.ho_type = re.search('用途：(.*)',ho).group(1)
            house.ho_room_type = re.search('户型：(.*)',ho).group(1)
            house.ho_build_size = re.search('总面积：(.*)',ho).group(1)
            if re.search('售价：(.*)',ho):
                house.ho_price = re.search('售价：(.*)',ho).group(1)
            else:
                house.ho_price = None
            house.insert_db()

