"""
url = http://www.aqhouse.net/projectlist.aspx?only=0&district=%u4EFB%u610F&use=%u4EFB%u610F&price=%u4EFB%u610F%20&housetype=%u4EFB%u610F&area=%u4EFB%u610F&by=%u697C%u76D8%u540D%u79F0&key=&opendate=
city :  安庆
CO_INDEX : 98
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree
from urllib import parse
import random

co_index = '98'
city_name = '安庆'

class Anqing(Crawler):
    def __init__(self):
        self.start_url = 'http://www.aqhouse.net/projectlist.aspx?only=0&district=%E4%BB%BB%E6%84%8F&use=%E4%BB%BB%E6%84%8F&price=%E4%BB%BB%E6%84%8F%20&housetype=%E4%BB%BB%E6%84%8F&area=%E4%BB%BB%E6%84%8F&by=%E6%A5%BC%E7%9B%98%E5%90%8D%E7%A7%B0&key=&opendate='
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            # 'Host':
            #     'www.aqhouse.net',
            # 'Cookie':
            #     'ASP.NET_SessionId=z3rcfs453shso2451rpltprm',
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

        index_res = requests.get(self.start_url,headers=self.headers)
        num = re.search('检索到.*?(\d+)',index_res.text).group(1)
        html = etree.HTML(index_res.text)
        viewstate = html.xpath("//input[@name='__VIEWSTATE']/@value")[0]
        even = html.xpath("//input[@name='__EVENTVALIDATION']/@value")[0]

        state = parse.quote_plus(viewstate)
        valid = parse.quote_plus(even)
        first = parse.quote('首页')

        formdata = {
            '__VIEWSTATE':viewstate,
            '__EVENTVALIDATION':even,
            'btnFirst':'首页',
            'txtPageSize' : int(num)
        }

        res = requests.post(self.start_url,data=formdata,headers=self.headers)
        comm_html = etree.HTML(res.text)
        comm_url_list = comm_html.xpath("//tr/td[4]/a/@href")
        comm_url_set = set(comm_url_list[:-2])
        for comm_url in comm_url_set:
            url = 'http://www.aqhouse.net/'+comm_url
            co_res = requests.get(url,headers=self.headers)
            co_id = self.comm_info(co_res,comm_url)
            bu_html = etree.HTML(co_res.text)
            bu_list = bu_html.xpath("//table[@rules='all']//tr")
            self.bu_info(bu_list,co_id)


    def comm_info(self,co_res,comm_url):
        con = co_res.text
        co = Comm(co_index)
        co.co_name = re.search('项目名称.*?value="(.*?)"',con,re.S|re.M).group(1)
        co_id = re.search('prjid=(\d+)',comm_url).group(1)
        co.co_id = co_id
        co.co_address = re.search('项目地址.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_develops = re.search('开发商.*?;">(.*?)</a',con,re.S|re.M).group(1)
        co.area = re.search('所属区.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_size = re.search('土地面积.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_build_size = re.search('建筑面积.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_plan_pro = re.search('规划许可证.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_land_use = re.search('土地证号.*?value="(.*?)"',con,re.S|re.M).group(1)
        co.co_all_house = re.search('>总套数.*?;">(\d+)</',con,re.S|re.M).group(1)
        co.insert_db()
        return  co_id

    def bu_info(self,bu_list,co_id):
        for bu_ in bu_list[1:]:
            bu = Building(co_index)
            bu.co_id = co_id
            bu.bu_num = bu_.xpath("./td/a/text()")[0]
            bu.bu_pre_sale = bu_.xpath("./td[2]/text()")[0]
            bu.bu_type = bu_.xpath("./td[4]/text()")[0]
            bu_url = bu_.xpath("./td/a/@href")[0]
            bu.bu_id = re.search('buildid=(\d+)',bu_url).group(1)
            bu.insert_db()
            self.ho_info(bu_url,co_id,bu.bu_id)

    def ho_info(self,url,co_id,bu_id):
        ho_url = 'http://www.aqhouse.net/' + url
        while True:
            try:
                proxy = self.proxies[random.randint(0,9)]
                ho_res = requests.get(ho_url,headers=self.headers,proxies=proxy)
                break
            except Exception as e:
                print(e)
        ho_html = etree.HTML(ho_res.text)
        room_list = ho_html.xpath("//td[@nowrap]/a/..")
        for room in room_list:
            try:
                room_info = room.xpath("./@title")[0]
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = room.xpath("./a/text()")[0]
                ho.ho_build_size = re.search('建筑面积：(.*?)平方米',room_info).group(1)
                ho.ho_true_size = re.search('套内面积：(.*?)平方米',room_info).group(1)
                ho.ho_share_size = re.search('分摊面积：(.*?)平方米',room_info).group(1)
                ho.ho_room_type = re.search('套型：(.*)',room_info).group(1)
                ho.ho_price = re.search('价格.*?：(.*?)元/平方米',room_info).group(1)

                ho.insert_db()
            except:
                print('房屋解析失败')




