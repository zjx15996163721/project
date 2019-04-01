"""
已经有id去重不请求详情页
"""
import requests
from auction import Auction
from lib.log import LogHandler
from sql_mysql import inquire, TypeAuction
from lib.mongo import Mongo
from lxml import etree
import datetime
import yaml
import re

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = 'gongpaiwang'
log = LogHandler(__name__)


class Gongpaiwang:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.list_info = []
        self.type_list = inquire(TypeAuction, source)

    def start_crawler(self):
        url = 'http://s.gpai.net/sf/search.do'
        try:
            response = requests.get(url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            city_list = tree.xpath('//a[@class="s-default"]')
            for city in city_list:
                city_url = city.xpath('@href')[0]
                city_name = city.xpath('text()')[0]
                self.get_region_info(city_url, city_name)
        except Exception as e:
            log.error('起始页页请求错误，url="{}",e="{}"'.format(url, e))

    def get_region_info(self, city_url, city_name):
        code = re.search('cityNum=(.*?)$', city_url).group(1)
        get_region_url = 'http://s.gpai.net/sf/AjaxHtml.do?Action=CITY&ID=' + code
        response = requests.get(get_region_url, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        region_xian = tree.xpath('//a')
        for region in region_xian:
            for i in self.type_list:
                html_type = i.html_type
                auction_type = i.auction_type
                region_url = 'http://s.gpai.net/sf/search.do?at=' + i.code + '&' + region.xpath('@href')[0]
                region_name = region.xpath('text()')[0]
                self.get_page_info(region_url, region_name, city_name, html_type, auction_type)

    def get_page_info(self, region_url, region_name, city_name, html_type, auction_type):
        try:
            response = requests.get(region_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            page = tree.xpath('/html/body/div/div[7]/div/div[4]/div/span[2]/label/text()')
            if page:
                page_1 = page[0]
                page_ = re.search('(\d+)', page_1, re.S | re.M).group(1)
            else:
                page_ = '1'
            self.get_auction_info(region_url, page_, region_name, city_name, html_type, auction_type)

        except Exception as e:
            log.error('起始页页请求错误，url="{}",e="{}"'.format(region_url, e))

    def get_auction_info(self, region_url, page, region_name, city_name, html_type, auction_type):
        for i in range(1, int(page) + 1):
            page_url = region_url + '&Page=' + str(i)
            response = requests.get(page_url, headers=self.headers)
            html = response.text
            if '当前未找到' in html:
                continue
            tree = etree.HTML(html)
            aution_list = tree.xpath('//div[@class="list-item"]')
            for aution_ in aution_list:
                aution_url = aution_.xpath('a/@href')[0]
                try:
                    aution_time = aution_.xpath('div[@class="gpai-infos"]/p[5]/span/text()')[0]
                    re.search('结束时间：(.*?)$', aution_time, re.S | re.M).group(1)
                except Exception as e:
                    aution_time = None
                aution_id = re.search('Web_Item_ID=(\d+)$', aution_url, re.S | re.M).group(1)
                is_exist = coll.find_one({'auction_id': str(aution_id), 'source': source})
                if is_exist:
                    log.info('id已存在，id="{}"'.format(str(aution_id)))
                    continue
                self.get_detail(aution_url, aution_id, aution_time, region_name, city_name, html_type, auction_type)

    def get_detail(self, aution_url, aution_id, aution_time, region_name, city_name, html_type, auction_type):
        info = []
        aution = Auction(source, auction_type)
        response = requests.get(aution_url, headers=self.headers)
        try:
            html = response.text
            tree = etree.HTML(html)
            aution.auction_id = aution_id
            aution.region = region_name
            aution.city = city_name
            aution.source_html = html
            aution.html_type = html_type
            try:
                aution.start_auction_price = float(tree.xpath('//*[@id="Price_Start"]/text()')[0].replace(',', ''))
            except Exception as e:
                aution.start_auction_price = None
            if 'item2' in aution_url:
                aution.auction_name = tree.xpath('//div[@class="d-m-title"]/b/text()')[0]
                aution.auction_level = tree.xpath('//div[@class="d-m-tb"]/table[1]/tr[1]/td[2]/text()')[0]
                try:
                    assess_value = tree.xpath('//div[@class="d-m-tb"]/table[1]/tr[4]/td[1]/text()')[0]
                    aution.assess_value = float(
                        re.search('(\d+),?(\d+)', assess_value, re.S | re.M).group(1).replace(',', ''))
                except Exception as e:
                    aution.assess_value = None
                earnest_money = tree.xpath('//div[@class="d-m-tb"]/table[1]/tr[3]/td[2]/text()')[0]
                aution.earnest_money = float(
                    re.search('(\d+),?(\d+)', earnest_money, re.S | re.M).group(1).replace(',', ''))
                court = tree.xpath('//td[@class="pr7"]/text()')[0]
                aution.court = re.search('法院：(.*?)$', court, re.S | re.M).group(1)
                aution.contacts = tree.xpath('//td[@valign="top"]/text()')[0]
                phone_number = tree.xpath('//td[@colspan="2"]/text()')[0]
                try:
                    aution.phone_number = re.search('联系电话：(.*?)$', phone_number, re.S | re.M).group(1)
                except Exception as e:
                    aution.phone_number = None
                info.append(tree.xpath('string(//div[@class="panel-con"]/div[@class="d-block"][2])'))
                info.append(tree.xpath('string(//div[@class="panel-con"]/div[@class="d-article d-article2"][3])'))
                aution.info = info
                if aution_time:
                    aution.auction_time = datetime.datetime.strptime(aution_time, "%Y-%m-%d %H:%M:%S")
            else:
                aution.auction_name = tree.xpath('//div[@class="DivItemName"]/text()')[0]
                aution.auction_level = tree.xpath('/html/body/div[1]/div[7]/div[2]/div[1]/div[2]/div[4]/li[4]/text()')[
                    0]
                try:
                    assess_value = tree.xpath('/html/body/div[1]/div[7]/div[2]/div[1]/div[2]/div[4]/li[5]/text()')[0]
                    aution.assess_value = float(
                        re.search('(\d+),?(\d+)', assess_value, re.S | re.M).group(1).replace(',', ''))
                except Exception as e:
                    aution.assess_value = None
                earnest_money = tree.xpath('/html/body/div[1]/div[7]/div[2]/div[1]/div[2]/div[4]/li[6]/text()')[0]
                aution.earnest_money = float(
                    re.search('(\d+),?(\d+)', earnest_money, re.S | re.M).group(1).replace(',', ''))
                court = tree.xpath('/html/body/div[1]/div[7]/div[2]/div[1]/div[2]/div[4]/li[8]/text()')[0]
                aution.court = re.search('法院：(.*?)$', court, re.S | re.M).group(1)
                area = tree.xpath('/html/body/div[1]/div[7]/div[2]/div[1]/div[2]/div[4]/li[2]/text()')[0]
                aution.area = float(re.search('(\d+)\.(\d+)', area, re.S | re.M).group(1).replace(',', ''))
                info.append(tree.xpath('string(//div[@id="Tab1"])'))
                info.append(tree.xpath('string(//div[@class="bootstrap-table"])'))
                aution.info = info
                if aution_time:
                    aution.auction_time = datetime.datetime.strptime(aution_time, "%Y-%m-%d %H:%M:%S")
            aution.insert_db()
        except Exception as e:
            log.error('解析错误，url="{}",e="{}"'.format(aution_url, e))
