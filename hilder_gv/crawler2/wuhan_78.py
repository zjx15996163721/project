"""
url = http://scxx.fgj.wuhan.gov.cn/xmqk.asp
city :  武汉
CO_INDEX : 78
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re
from lxml import etree
from urllib import parse
import time
from lib.log import LogHandler
from backup.proxy_connection import Proxy_contact

city = '武汉'
co_index = '78'
log = LogHandler('wuhan_78')

class Wuhan(Crawler):
    def __init__(self):
        self.start_url = 'http://scxx.fgj.wuhan.gov.cn/xmqk.asp'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        proxy = Proxy_contact(app_name='wuhan',method='get',url=self.start_url,headers=self.headers)
        # index_res = requests.get(self.start_url,headers=self.headers,)
        index_res = proxy.contact()
        con = index_res.decode('gbk')
        page = re.search('共搜索到<FONT.*?(\d+)</FONT>页',con).group(1)

        for i in range(1,int(page)+1):

            url = self.start_url + "?page=" + str(i)
            page_proxy = Proxy_contact(app_name='wuhan',method='get',url=url,headers=self.headers)
            # res = requests.get(url,headers=self.headers,)
            res = page_proxy.contact()
            html = etree.HTML(res.decode('gbk'))
            temp_url_list = html.xpath("//tr//td/a/@href")
            self.comm_info(temp_url_list)
            time.sleep(2)

    def comm_info(self,url_list):
        for temp_url in url_list:
            try:
                comm = Comm(co_index)
                comm.co_id = re.search('Jh=(.*?\d+)',temp_url).group(1)
                parse_url = parse.quote(comm.co_id,encoding='gbk')
                comm_url = 'http://scxx.fgj.wuhan.gov.cn/3.asp?DengJh=' + parse_url
                proxy = Proxy_contact(app_name='wuhan', method='get', url=comm_url,headers=self.headers)
                res = proxy.contact()
                # res = requests.get(comm_url,headers=self.headers)
                con = res.decode('gb18030')
                # comm.co_id = re.search('Jh=(.*?)',temp_url).group(1)
                comm.co_name = re.search('项目名称.*?">(.*?)<',con,re.S|re.M).group(1)
                comm.co_all_house = re.search('套数.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
                comm.co_address = re.search('坐落.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_build_start_time = re.search('开工时间.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_build_end_time = re.search('竣工时间.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_size = re.search('用地面积.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
                comm.co_build_size = re.search('建筑面积.*?">(.*?)&nbsp',con,re.S|re.M).group(1)
                comm.co_volumetric = re.search('容积率.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_develops = re.search('开发企业</TD>.*?">(.*?)</TD',con,re.S|re.M).group(1)
                comm.co_land_use = re.search('土地使用证号.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_plan_useland = re.search('用地规划许可证号.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_plan_project = re.search('工程规划许可证号.*?">(.*?)</',con,re.S|re.M).group(1)
                comm.co_work_pro = re.search('施工许可证号.*?">(.*?)</',con,re.S|re.M).group(1)

                comm.insert_db()
                log.debug('{}插入成功'.format(comm.co_name))
            except Exception as e:
                log.error('小区错误{}'.format(e))
                continue
            build_detail = re.sub('3','4',comm_url)
            self.build_info(build_detail,comm.co_id)

    def build_info(self,build_detail,co_id):
        proxy = Proxy_contact(app_name='wuhan',method='get',url=build_detail,headers=self.headers)
        # build_res = requests.get(build_detail,headers=self.headers)
        build_res = proxy.contact()
        html = etree.HTML(build_res.decode('gb18030'))
        info_list = html.xpath("//tr[@bgcolor='#FFFFFF']")
        for info in info_list:
            try:
                bu = Building(co_index)
                bu.co_id = co_id
                bu.bu_floor = info.xpath('./td[3]/text()')[0]
                bu.bu_all_house = info.xpath('./td[4]/text()')[0]
                bu.bu_num = info.xpath('./td//span/text()')[0]
                temp_url = info.xpath('./td/a/@href')[0]
                bu.bu_id = re.search('HouseDengjh=(.*?\d+)',temp_url).group(1)
                bu.insert_db()
            except Exception as e:
                log.error('楼栋错误{}'.format(e))
                continue
            a = parse.quote(re.search('DengJh=(.*?\d+)&',temp_url).group(1),encoding='gbk')
            b = parse.quote(re.search('HouseDengjh=(.*?\d+)',temp_url).group(1),encoding='gbk')
            bu_url = 'http://scxx.fgj.wuhan.gov.cn/5.asp?DengJh=' + a + '&HouseDengjh=' + b
            self.house_info(bu.bu_id,bu_url,co_id)
            time.sleep(3)

    def house_info(self,bu_id,bu_url,co_id):
        proxy = Proxy_contact(app_name='wuhan',method='get',url=bu_url,headers=self.headers)
        res = proxy.contact()
        # res = requests.get(bu_url,headers=self.headers)
        html = etree.HTML(res.decode('gb18030'))
        con = html.xpath("//tr[@bgcolor='#FFFFFF']")
        for i in con :
            try:
                ho = House(co_index)
                ho.bu_id = bu_id
                ho.co_id = co_id
                ho.ho_floor = i.xpath("./td/text()")[2]
                house_num_list = i.xpath("./td[@bgcolor='#CCFFFF']")
                for house_num in house_num_list:
                    ho.ho_name = house_num.xpath(".//a/text()")[0]
                    ho.insert_db()
            except Exception as e:
                log.error('房号错误{}'.format(e))

