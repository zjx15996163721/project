"""
url = http://tmsf.qzfdcgl.com/newhouse/property_searchall.htm
city :  衢州
CO_INDEX : 191
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree

co_index = '191'
city_name = '衢州'

class Quzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://tmsf.qzfdcgl.com/newhouse/property_searchall.htm'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            # 'Referer': ''
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
                       page_count_rule='页数.*?/(\d+)',
                       )
        page = b.get_page_count()

        for i in range(1,int(page)+1):
            formdata = {
                'page':i,
                'keytype':1,
            }
            res = requests.post(self.start_url,data=formdata,headers=self.headers)
            html = etree.HTML(res.text)
            url_list = html.xpath("//h3/a")
            self.co_parse(url_list)

    def co_parse(self,url_list):
        for url in url_list:
            try:
                co_url = url.xpath("./@href")[0]
                new_url = "http://tmsf.qzfdcgl.com" + co_url
                co_res = requests.get(new_url,headers=self.headers)
                con = co_res.text
                co = Comm(co_index)
                co.co_id = re.search('property_(.*?)_info',co_url).group(1)
                co.co_name = re.search('楼盘名称：</span>(.*)',con).group(1)
                co.co_develops = re.search('项目公司：</span>(.*)',con).group(1)
                co.co_address = re.search('物业地址：</span>(.*?)</p',con,re.S|re.M).group(1)
                co.area = re.search('所属城区：</span>(.*)',con).group(1)
                co.insert_db()
                sid = re.search('property_(\d+)_',co_url).group(1)
                propertyid = re.search('(\d+)_info',co_url).group(1)
                bu_url = new_url.replace('info','price')
                res = requests.get(bu_url,headers=self.headers)
                bu_html = etree.HTML(res.text)
                bu_idlist = bu_html.xpath("//dd[@id='building_dd']/a")
            except:
                continue
            for bu_ in bu_idlist[1:]:
                id = bu_.xpath("./@id")[0]
                bu_id = re.search('.*?(\d+)',id).group(1)
                bu = Building(co_index)
                bu.bu_id = bu_id
                bu.co_id = co.co_id
                bu.bu_num = bu_.xpath("./text()")[0]

                bu.insert_db()
                self.house_parse(bu_id,co.co_id,sid,propertyid)

    def house_parse(self,bu_id,co_id,sid,propertyid):
        data = {
            'propertyid':propertyid,
            'sid':sid,
            'buildingid':bu_id,
            'tid':'price',
            'page':1
        }
        res = requests.post('http://tmsf.qzfdcgl.com/newhouse/property_pricesearch.htm',data=data,headers=self.headers)
        page = re.search('页数.*?/(\d+)',res.text).group(1)
        for i in range(1,int(page)+1):
            data['page'] = i
            ho_res = requests.post('http://tmsf.qzfdcgl.com/newhouse/property_pricesearch.htm', data=data, headers=self.headers)
            con  = ho_res.text
            ho_html = etree.HTML(con)
            house_list = ho_html.xpath("//tr[@onmouseout]")
            for house in house_list:
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = house.xpath("./td[3]/a/div/text()")[0]
                ho.unit = house.xpath("./td[2]/a/div/text()")[0]
                buildsize = house.xpath("./td[4]/a/div/span/@class")
                truesize = house.xpath("./td[5]/a/div/span/@class")
                price = house.xpath("./td[9]/a/div/span/@class")
                ho.ho_build_size = self.number_replace(buildsize)
                ho.ho_true_size = self.number_replace(truesize)
                ho.ho_price = self.number_replace(price)
                ho.insert_db()

    def number_replace(self,number_list):
        number_dict = {
            'numberone':'1',
            'numbertwo':'2',
            'numberthree':'3',
            'numberfour':'4',
            'numberfive':'5',
            'numbersix':'6',
            'numberseven':'7',
            'numbereight':'8',
            'numbernine':'9',
            'numberzero':'0',
            'numberdor':'.'
        }
        i = ''
        for number in number_list:
            num = number_dict[number]
            i =  i + num
        return i





