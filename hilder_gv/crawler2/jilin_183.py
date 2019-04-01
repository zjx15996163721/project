"""
url = http://www.ccfdw.gov.cn/ecdomain/lpcs/
city :  吉林
CO_INDEX : 183
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree

from lib.log import LogHandler

co_index = '183'
city_name = '吉林'
log = LogHandler('jilin')

class Jilin(Crawler):
    def __init__(self):
        self.start_url = 'http://www.ccfdw.gov.cn/ecdomain/lpcs/'
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
        start_url = self.start_url + "searchSpf.jsp?nowPage=1"
        b = AllListUrl(first_page_url=start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='/(\d+)页',
                       )
        page = b.get_page_count()
        for i in range(1,int(page)+1):
            url = self.start_url + "searchSpf.jsp?nowPage=" +str(i)
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content.decode())
            url_list = html.xpath("//b/a/@href")
            for comm_temp in url_list:
                try:
                    comm_url = self.start_url + comm_temp.replace("./xmxxmainNew",'xmxx/xmjbxx')
                    com_res = requests.get(comm_url,headers=self.headers)
                    con = com_res.content.decode('gbk')
                    co = Comm(co_index)
                    co.co_id = re.search('Id_xmxq=(.*)',comm_temp).group(1)
                    co.co_name = re.search('3a3a3a">(.*?)</b',con).group(1)
                    co.co_address = re.search('项目地址.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_develops = re.search('开 发 商.*?">(.*?)</td',con,re.S|re.M).group(1)
                    co.co_all_house = re.search('总 套 数.*?<td>(.*?)</td',con,re.S|re.M).group(1)
                    co.co_green = re.search('绿 化 率.*?<td>(.*?)</td',con,re.S|re.M).group(1)
                    co.co_volumetric = re.search('容 积 率.*?<td>(.*?)</td',con,re.S|re.M).group(1)
                    try:
                        co.co_build_size = re.search('建设规模.*?" >(.*?)平',con,re.S|re.M).group(1)
                    except:
                        co.co_build_size  = None
                    co.insert_db()
                except Exception as e:
                    log.error('{}小区错误{}'.format(comm_temp,e))
                self.build_parse(co.co_id)

    def build_parse(self,co_id):
        list_url = 'http://www.ccfdw.gov.cn/ecdomain/lpcs/xmxx/loulist.jsp?Id_xmxq=' + co_id
        res = requests.get(list_url,headers=self.headers)
        con = res.content.decode()
        build_id_list = re.findall("searchByLid\('(\d+)'\)",con)
        for build_id in build_id_list:
            try:
                bu_url = 'http://www.ccfdw.gov.cn/ecdomain/lpcs/xmxx/lpbxx_new.jsp?lid='+ build_id
                bu_res = requests.get(bu_url,headers=self.headers)
                bu_con = bu_res.content.decode('gbk')
                bu = Building(co_index)
                bu.co_id = co_id
                bu.bu_id = build_id
                bu.bu_num = re.search('楼栋名称.*?">(.*?)</td',bu_con,re.S|re.M).group(1)
                bu.bu_all_house = re.search('总套数.*?">总(.*?)套</td',bu_con,re.S|re.M).group(1)
                bu.bu_floor = re.search('地上层数.*?">共(.*?)层</td',bu_con,re.S|re.M).group(1)
                bu.bu_build_size = re.search('总建筑面积.*?">(.*?)</td',bu_con,re.S|re.M).group(1)
                bu.bu_pre_sale = re.search("searchysxk\('(.*?)'\)",bu_con,re.S|re.M).group(1)
                bu.bu_type = re.search('房屋用途.*?">(.*?)</td',bu_con,re.S|re.M).group(1)
                bu.insert_db()
            except Exception as e:
                log.error('{}楼栋错误{}'.format(build_id,e))
            self.house_parse(co_id,build_id,bu_con)

    def house_parse(self,co_id,bu_id,bu_con):

        name_list = re.findall('<a style.*?\)>(.*?)</a',bu_con)
        for name in name_list:
            ho = House(co_index)
            ho.co_id = co_id
            ho.bu_id = bu_id
            ho.ho_name = name
            ho.insert_db()





