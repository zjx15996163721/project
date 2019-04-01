"""
url = http://spf.szfcweb.com/szfcweb/(S(hdeijxnxs01rlpun22pnfha0))/DataSerach/SaleInfoProListIndex.aspx
city :  苏州
CO_INDEX : 161
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
import time
from lxml import etree
from lib.log import LogHandler
import random

co_index = '161'
city_name = '苏州'
log = LogHandler('苏州')


class Suzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://spf.szfcweb.com/szfcweb/(S(hdeijxnxs01rlpun22pnfha0))/DataSerach/SaleInfoProListIndex.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Cookie':
                '_gscu_1135684666=29633282eu1o1k12'
        }

    def start_crawler(self):
        s = requests.session()
        res = s.get(self.start_url)
        path_url = 'http://spf.szfcweb.com'+res.request.path_url
        html = etree.HTML(res.content.decode())
        viewstate = html.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
        generator = html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
        validation = html.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
        select = '查询'
        for region in ['工业园区','吴中区','高新区','相城区','姑苏区','吴江区']:
            formdata = {'__VIEWSTATE':viewstate,
                        '__VIEWSTATEGENERATOR':generator,
                        '__EVENTVALIDATION':validation,
                        'ctl00$MainContent$ddl_RD_CODE':region,
                        'ctl00$MainContent$bt_select':select,
                        }
            index_res = s.post(path_url,data=formdata,headers=self.headers)
            page = re.search('nbsp共&nbsp(\d+)&nbsp页',index_res.text).group(1)
            data = {}
            for i in range(1,int(page)+1):
                if i==1:
                    index_html = etree.HTML(index_res.text)
                    self.co_parse(index_html,path_url,region)
                    view_state = index_html.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
                    generator_ = index_html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
                    validation_ = index_html.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
                    data = {'__VIEWSTATE':view_state,
                        '__VIEWSTATEGENERATOR':generator_,
                        '__EVENTVALIDATION':validation_,
                        'ctl00$MainContent$ddl_RD_CODE':region,
                        '__EVENTTARGET':'ctl00$MainContent$OraclePager1$ctl12$PageList',
                        'ctl00$MainContent$OraclePager1$ctl12$PageList':1,}
                else:
                    page_res = requests.post(path_url,data=data)
                    page_html = etree.HTML(page_res.text)
                    view_state = page_html.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
                    generator_ = page_html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
                    validation_ = page_html.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
                    data = {'__VIEWSTATE': view_state,
                            '__VIEWSTATEGENERATOR': generator_,
                            '__EVENTVALIDATION': validation_,
                            'ctl00$MainContent$ddl_RD_CODE': region,
                            '__EVENTTARGET': 'ctl00$MainContent$OraclePager1$ctl12$PageList',
                            'ctl00$MainContent$OraclePager1$ctl12$PageList': i,}
                    self.co_parse(page_html,path_url,region)

    def co_parse(self,page_html,path_url,region):
        url_list = page_html.xpath('//td//a/@href')
        for url in url_list[:9]:
            try:
                co_url = path_url.replace('SaleInfoProListIndex.aspx','')+url
                self.headers['Referer'] = path_url
                co_res = requests.get(co_url,headers=self.headers)
                co = Comm(co_index)
                co.area = region
                co.co_name = re.search('项目名称.*?NAME">(.*?)</span',co_res.text,re.S|re.M).group(1)
                co.co_id = re.search('ID=(.*)',url).group(1)
                co.co_develops = re.search('公司名称.*?Com">(.*?)</span',co_res.text,re.S|re.M).group(1)
                co.co_address = re.search('项目地址.*?Add">(.*?)</span',co_res.text,re.S|re.M).group(1)
                co.insert_db()
                page = re.search('共&nbsp(\d+)&nbsp页',co_res.text).group(1)
            except:
                log.error("{}访问失败".format(co_url))
                continue
            self.bu_parse(co.co_id,page,co_url,co_res,path_url)
            time.sleep(random.randint(1,5))

    def bu_parse(self,co_id,page,co_url,co_res,path_url):
        html = etree.HTML(co_res.text)
        viewstate = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
        generator = html.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")[0]
        valid = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
        formdata = {
            "__VIEWSTATE":viewstate,
            "__EVENTTARGET":'ctl00$MainContent$OraclePager1$ctl11$PageList',
            "__VIEWSTATEGENERATOR":generator,
            "__EVENTVALIDATION": valid,
            "ctl00$MainContent$OraclePager1$ctl11$PageList":0
        }
        self.headers['Referer'] = co_url

        for i in range(1,int(page)+1):
            page_res = requests.post(co_url,data=formdata,headers=self.headers)
            page_html = etree.HTML(page_res.text)
            view_state = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
            generator_ = html.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")[0]
            valid_ = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
            formdata = {
                "__VIEWSTATE": view_state,
                "__EVENTTARGET": 'ctl00$MainContent$OraclePager1$ctl11$PageList',
                "__VIEWSTATEGENERATOR": generator_,
                "__EVENTVALIDATION": valid_,
                "ctl00$MainContent$OraclePager1$ctl11$PageList": i - 1
            }

            bu_list = page_html.xpath("//table[@id='ctl00_MainContent_OraclePager1']//tr")

            for bu in bu_list[1:]:
                build = Building(co_index)
                build.co_id = co_id
                build.bu_num = bu.xpath("./td/a/text()")[0]
                build.bu_build_size = bu.xpath("./td[2]/text()")[0]
                build.bu_floor = bu.xpath("./td[4]/text()")[0]
                build.bu_all_house = bu.xpath("./td[3]/text()")[0]
                tmp_url = bu.xpath("./td/a/@href")[0]
                build.bu_id = re.search('PBTAB_ID=(.*?)&',tmp_url).group(1)
                build.insert_db()
                house_url = path_url.replace('SaleInfoProListIndex.aspx','')+tmp_url
                self.ho_parse(co_id,build.bu_id,house_url)

    def ho_parse(self,co_id,bu_id,house_url):
        res = requests.get(house_url,headers=self.headers)
        html = etree.HTML(res.text)
        ho_list = html.xpath("//td[@align]")
        for house in ho_list:
            ho = House(co_index)
            ho.co_id = co_id
            ho.bu_id = bu_id
            ho.ho_name = house.xpath("./text()")[0]
            ho.insert_db()





