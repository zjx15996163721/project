"""
人民法院诉讼资产网
已经有id去重不请求详情页
http://www1.rmfysszc.gov.cn/projects.shtml?dh=3&gpstate=1&wsbm_slt=1
"""
import requests
from sql_mysql import inquire, CityAuction, TypeAuction
import re
from lxml import etree
from auction import Auction
from lib.log import LogHandler
from lib.mongo import Mongo
import yaml
import datetime

setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

auction_type = '房产'
source = 'rmfysszc'
url = 'http://www1.rmfysszc.gov.cn/ProjectHandle.shtml'
log = LogHandler(__name__)


class Rmfysszc:
    def __init__(self):
        self.headers = {
            'Referer': 'http://www1.rmfysszc.gov.cn/projects.shtml?dh=3&gpstate=1&wsbm_slt=1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.type_list = inquire(TypeAuction, source)
        self.city_list = inquire(CityAuction, source)

    def start_crawler(self):
        # get all page data 获得所有页面的data
        list_data = self.get_data()
        for data in list_data:
            html_type = data[1]
            auction_type = data[2]
            province = data[3]
            city = data[4]
            try:
                response = requests.post(url=url, data=data[0], headers=self.headers)
                html = response.text
                tree = etree.HTML(html)
                if '暂无您查询的标的物' in html:
                    log.info('此区域没有数据,province="{}",city="{}",region="{}"'.format(province, city, data[0]['area']))
                    continue
                page_str = tree.xpath('//div[@id="page"]/a/@onclick')
                if not page_str:
                    page_str = ['1']
                page_num = re.search('(\d+)', page_str[-1], re.S | re.M).group(1)
                for i in range(1, int(page_num) + 1):
                    data[0]['page'] = str(i)
                    response = requests.post(url=url, data=data[0], headers=self.headers)
                    html = response.text
                    tree = etree.HTML(html)
                    info_list = tree.xpath('//*[@class="product"]')
                    for info in info_list:
                        id_ = info.xpath('@id')[0]
                        is_exist = coll.find_one({'auction_id': id_, 'source': source})
                        if is_exist:
                            log.info('id已存在，id="{}"'.format(id_))
                            continue
                        try:
                            auction_time = info.xpath('div[2]/p[3]/span/text()')[0]
                        except Exception as e:
                            auction_time = None
                        self.get_detail(id_, auction_time, html_type, auction_type, province, city, data[0]['area'])
            except Exception as e:
                log.error('网络请求错误，url="{}",data="{}",e="{}"'.format(url, data[0], e))

    def get_detail(self, id_, auction_time, html_type, auction_type, province, city, region):
        auction = Auction(source=source, auction_type=auction_type)
        auction.html_type = html_type
        auction.auction_type = auction_type
        auction.province = province
        auction.city = city
        auction.region = region
        detail_url = 'http://www1.rmfysszc.gov.cn/Handle/' + id_ + '.shtml'
        try:
            response = requests.get(detail_url, headers=self.headers)
            html = response.content.decode()
            auction.source_html = html
            info_list = []
            try:
                if 'GetRecord()' in html:
                    tree = etree.HTML(html)
                    auction.auction_name = tree.xpath('//div[@id="Title"]/h1/text()')[0]
                    start_auction_price = tree.xpath('//*[@id="price"]/div[1]/span/text()')[0]
                    auction.start_auction_price = self.get_float(start_auction_price)
                    assess_value = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[1]/td/span[2]/text()')[0]
                    try:
                        auction.assess_value = self.get_float(assess_value)
                    except Exception as e:
                        auction.assess_value = None
                    earnest_money = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[2]/td/span[2]/text()')[0]
                    auction.earnest_money = self.get_float(earnest_money)
                    announcement_date = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[3]/td/span/text()')[0]
                    announcement_date_ = re.search(': (.*?)$', announcement_date, re.S | re.M).group(1)
                    auction.announcement_date = datetime.datetime.strptime(announcement_date_, "%Y.%m.%d")
                    auction_level = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[4]/td/span/text()')[0]
                    auction.auction_level = re.search(': (.*?)$', auction_level, re.S | re.M).group(1)
                    court = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[1]/td/span/text()')[0]
                    auction.court = re.search(': (.*?)$', court, re.S | re.M).group(1)
                    info_list.append(tree.xpath('string(//*[@id="bdjs11"])').encode().decode())
                    info_list.append(tree.xpath('string(//*[@id="jjjl"])').encode().decode())
                    contacts = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[2]/td/span/text()')[0]
                    auction.contacts = re.search(': (.*?)$', contacts, re.S | re.M).group(1)
                    phone_number = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[3]/td/span/text()')[0]
                    auction.phone_number = re.search(': (.*?)$', phone_number, re.S | re.M).group(1)
                    auction.info = info_list
                    try:
                        auction.build_type = tree.xpath('//*[@id="bdjs11"]/table[1]/tr[2]/td[4]/text()')[0]
                    except Exception as e:
                        auction.build_type = None
                    auction.auction_id = id_
                    auction.auction_time = self.get_date(date=auction_time)
                    auction.insert_db()
                elif 'bmnumber()' in html:
                    tree = etree.HTML(html)
                    auction.auction_name = tree.xpath('//div[@id="Title"]/h1/text()')[0]
                    start_auction_price = tree.xpath('//*[@id="price"]/div[1]/span/text()')[0]
                    auction.start_auction_price = self.get_float(start_auction_price)
                    assess_value = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[1]/td/span[2]/text()')[0]
                    auction.assess_value = self.get_float(assess_value)
                    earnest_money = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[2]/td/span[2]/text()')[0]
                    auction.earnest_money = self.get_float(earnest_money)
                    announcement_date = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[3]/td/span/text()')[0]
                    announcement_date_ = re.search(': (.*?)$', announcement_date, re.S | re.M).group(1)
                    auction.announcement_date = datetime.datetime.strptime(announcement_date_, "%Y-%m-%d")
                    auction_level = tree.xpath('//*[@id="bg1"]/div[1]/table/tr[4]/td/span/text()')[0]
                    auction.auction_level = re.search(': (.*?)$', auction_level, re.S | re.M).group(1)
                    court = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[1]/td/span/text()')[0]
                    auction.court = re.search(': (.*?)$', court, re.S | re.M).group(1)
                    info_list.append(tree.xpath('string(//*[@id="bdjs"])').encode().decode())
                    contacts = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[2]/td/span/text()')[0]
                    auction.contacts = re.search(': (.*?)$', contacts, re.S | re.M).group(1)
                    phone_number = tree.xpath('//*[@id="bg1"]/div[2]/table/tr[3]/td/span/text()')[0]
                    auction.phone_number = re.search(': (.*?)$', phone_number, re.S | re.M).group(1)
                    auction.info = info_list
                    try:
                        auction.build_type = tree.xpath('//*[@id="bdjs11"]/table[1]/tr[2]/td[4]/text()')[0]
                    except Exception as e:
                        auction.build_type = None
                    auction.auction_id = id_
                    auction.auction_time = self.get_date(date=auction_time)
                    auction.insert_db()
                else:
                    tree = etree.HTML(html)
                    auction.auction_name = tree.xpath('//*[@id="xmgg"]/div/div[1]/text()')[0]
                    assess_value = tree.xpath('/html/body/div[6]/table/tr/td/ul/li[3]/span/text()')[0]
                    auction.assess_value = self.get_float(assess_value)
                    announcement_date = tree.xpath('/html/body/div[6]/table/tr/td/ul/li[2]/span/text()')[0]
                    try:
                        auction.announcement_date = datetime.datetime.strptime(announcement_date, "%Y-%m-%d")
                    except Exception as e:
                        auction.announcement_date = datetime.datetime.strptime(announcement_date, "%Y/%m/%d")
                    auction.court = tree.xpath('/html/body/div[6]/table/tr/td/ul/li[1]/span/text()')[0]
                    info_list.append(tree.xpath('string(//*[@id="bdxx"]/div)').encode().decode())
                    info_list.append(tree.xpath('string(//*[@id="tjzl"]/div/div[2])').encode().decode())
                    auction.contacts = tree.xpath('/html/body/div[6]/table/tr/td/ul/li[4]/span/text()')[0]
                    auction.phone_number = tree.xpath('/html/body/div[6]/table/tr/td/ul/li[5]/span/text()')[0]
                    auction.info = info_list
                    try:
                        auction.build_type = tree.xpath('//*[@id="bdxx"]/div/div[2]/table/tr[2]/td[3]/text()')[0]
                    except Exception as e:
                        auction.build_type = None
                    auction.auction_id = id_
                    auction.auction_time = self.get_date(date=auction_time)
                    auction.insert_db()
            except Exception as e:
                log.error('解析错误,url="{}",e="{}"'.format(detail_url, e))

        except Exception as e:
            log.error('详情页请求错误,url="{}",e="{}"'.format(detail_url, e))

    def get_float(self, num_):
        return float(re.search('(\d+\.?\d?)', num_.encode().decode(),
                               re.S | re.M).group(1)) * 10000

    def get_date(self, date):
        if not date:
            return None
        if '年' in date:
            date_info = datetime.datetime.strptime(date, "%Y年%m月%d日%H:%M")
        else:
            date_str = '2018年' + date
            date_info = datetime.datetime.strptime(date_str, "%Y年%m月%d日%H:%M")
        return date_info

    def get_data(self):
        list_data = []
        for type_ in self.type_list:
            html_type = type_.html_type
            auction_type = type_.auction_type
            for area in self.city_list:
                province = area.province
                city = area.city
                data = {
                    'type': str(type_.code),
                    'name': '',
                    'area': area.code,
                    'state': '0',
                    'time': '0',
                    'time1': '',
                    'time2': '',
                    'money': '',
                    'money1': '',
                    'number': '0',
                    'fid1': '',
                    'fid2': '',
                    'fid3': '',
                    'order': '0',
                    'page': '1',
                    'include': '0'
                }
                list_data.append((data, html_type, auction_type, province, city))
        return list_data


if __name__ == '__main__':
    r = Rmfysszc()
    r.start_crawler()
