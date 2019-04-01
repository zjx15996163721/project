# @Author  :
# @city    : 
# @C0_INDEX: 
# @url     :
"""
url = http://www.hufdc.com/presell.jspx?pageno=1&keyword=
city : 湖州
CO_INDEX : 19
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
import json

co_index = 19
class Huzhou(Crawler):
    def __init__(self):
        self.url = "http://www.hufdc.com/presell.jspx?pageno=10000"
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='" >(\d+)</a>&nbsp',
                       )
        page = b.get_page_count()

        for i in range(1,int(page)+1):   #翻页
            url = "http://www.hufdc.com/presell.jspx?pageno="+str(i)
            response = requests.get(url,headers=self.headers)

            url_html = etree.HTML(response.text)
            self.comm_parse(url_html)

    def comm_parse(self,url_html):

        temp_url = "http://hu.tmsf.com/newhouse/property_330500_0_price.htm?presellname="
        co_info_list = url_html.xpath("//div[@class='lbox']//tr")[1:-1]
        for co_detail in co_info_list:
            try:
                co_develops = co_detail.xpath("./td/text()")[2]
                co_pre_sale = co_detail.xpath("./td/a/text()")[0]
                co_name = co_detail.xpath("./td/text()")[1]
                co_pre_sale_date = co_detail.xpath("./td/text()")[3]
                word = co_detail.xpath("./td/a/@href")[0]
                part_url = re.search("tolp\('(.*?)'\)",word).group(1)

                comm_url = temp_url + self.escape(part_url)

                self.comm_crawler(comm_url,co_develops,co_pre_sale,co_name,co_pre_sale_date )
            except:
                continue

    # def build(self,comm_html,sid):
    #     bu = Building(co_index)
    #
    #     bu_num = comm_html.xpath("//div[@id='building_dd']//a")[1:]
    #     bu_info = {}
    #     bu_num_list = []
    #     for bu_ in bu_num:
    #         bu.bu_num = bu_.xpath("./text()")[0]
    #         bu_id = bu_.xpath("./@id")[0]
    #         bu.bu_id = re.search('\d+',bu_id).group(0)
    #         bu.co_id = sid
    #         bu.insert_db()
    #         bu_info[bu.bu_num] = bu.bu_id
    #         bu_num_list.append(bu.bu_num)
    #     return bu_info,bu_num_list

    def comm_info(self,co_develops,co_pre_sale,co_name,co_pre_sale_date,sid):
        co = Comm(co_index)
        co.co_pre_sale = co_pre_sale
        co.co_id = sid
        co.co_name =co_name
        co.co_pre_sale_date=co_pre_sale_date
        co.co_develops = co_develops
        co.insert_db()

    def comm_crawler(self,comm_url,co_develops,co_pre_sale,co_name,co_pre_sale_date):
        ho = House(co_index)
        comm_res = requests.get(comm_url,headers=self.headers)
        comm_html = etree.HTML(comm_res.text)
        value = comm_html.xpath("//input[@id='propertyid']/@value")[0]
        sid = comm_html.xpath("//input[@id='sid']/@value")[0]
        # detail_url = "http://hu.tmsf.com/newhouse/property_"+str(sid)+"_"+str(value)+"_price.htm"

        bu = Building(co_index)
        bu_num = comm_html.xpath("//div[@id='building_dd']//a")[1:]
        # bu_info,bu_num_list = self.build(comm_html,value)
        self.comm_info(co_develops,co_pre_sale,co_name,co_pre_sale_date,value)
        # page_html = requests.get(detail_url,headers=self.headers)
        for bu_ in bu_num:
            bu.bu_num = bu_.xpath("./text()")[0]
            bu_id = bu_.xpath("./@id")[0]
            bu.bu_id = re.search('\d+', bu_id).group(0)
            bu.co_id = value
            bu.insert_db()
            detail_url = "http://hu.tmsf.com/newhouse/property_" + str(sid) + "_" + str(value) + "_price.htm?buildingid="+str(bu.bu_id)
            page_html = requests.get(detail_url, headers=self.headers)

            page = re.search('页数 \d+/(\d+)',page_html.text).group(1)
            for i in range (1,int(page)+1):
                detail_url = detail_url+"?page="+str(i)

                detail_res = requests.get(detail_url,headers=self.headers)
                house_html = etree.HTML(detail_res.text)
                house_url_list = house_html.xpath("//td[@width='100']/a/@href")
                house_bu_num = house_html.xpath("//td[@width='100']/a/text()")
                house_name = house_html.xpath("//td[@width='101'][1]/a/div/text()")

                for index in range(1,len(house_url_list)+1):
                    try:
                        ho.bu_num = house_bu_num[index]  # 楼号 栋号
                        house_url = "http://hu.tmsf.com" + house_url_list[index]
                        house_res = requests.get(house_url,headers=self.headers)
                        house_html = house_res.text
                        ho.bu_id = bu.bu_id
                        ho.co_id = re.search('楼盘主页.*?_\d+_(\d+)_info',house_html).group(1) # 小区id
                        ho.ho_name = house_name[index]  # 房号：3单元403
                        # ho.ho_num =  re.search('_(\d+).htm',house_url).group(1) # 房号id

                        ho.ho_type = re.search('房屋用途：.*?>(.*?)<',house_html).group(1)  # 房屋类型：普通住宅 / 车库仓库
                        ho.ho_floor = re.search('第(.*?)层',house_html).group(1)

                        build_text = re.search('建筑面积：(.*?)平方米',house_html).group(1)
                        build_num = re.findall('class="(.*?)"',build_text)
                        ho.ho_build_size = self.number(build_num)  # 建筑面积

                        size_text = re.search('套内面积：(.*?)平方米',house_html).group(1)
                        size_num = re.findall('class="(.*?)"',size_text)
                        ho.ho_true_size = self.number(size_num)  # 预测套内面积,实际面积

                        price_text = re.search('总　　价：(.*?)万元',house_html).group(1)# 价格
                        price_num = re.findall('class="(.*?)"',price_text)
                        ho.ho_price = self.number(price_num)

                        ho.insert_db()
                    except:
                        continue

    def number(self,x):
        num_compile = {
            "numberzero":"0",
            "numberone":"1",
            "numbertwo":"2",
            "numberthree":"3",
            "numberfour":"4",
            "numberfive":"5",
            "numbersix":"6",
            "numberseven":"7",
            "numbereight":"8",
            "numbernine":"9",
            "numberdor":".",
            "ssnumberzero": "0",
            "ssnumberone": "1",
            "ssnumbertwo": "2",
            "ssnumberthree": "3",
            "ssnumberfour": "4",
            "ssnumberfive": "5",
            "ssnumbersix": "6",
            "ssnumberseven": "7",
            "ssnumbereight": "8",
            "ssnumbernine": "9",
            "ssnumberdor": "."
        }
        str=''
        for i in x:
            num = num_compile[i]
            str = str +num
        return str

    def escape(self, x):
        a = json.dumps(x).upper()
        a = a.replace("\\", "%25")
        a = a.replace('U', 'u')
        a = json.loads(a)
        return a

