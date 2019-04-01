"""
已经有id去重不请求详情页
"""
import yaml
import requests
from lib.log import LogHandler
from lib.mongo import Mongo
from lxml import etree
from auction import Auction, check_auction
from sql_mysql import inquire, CityAuction, TypeAuction
import re
import datetime

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = 'zhupaiwang'
log = LogHandler(__name__)


class Zhupaiwang:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
            'Referer': 'https://ningbo.51zhupai.com/house'
        }
        self.city_code = inquire(CityAuction, source)
        self.map = inquire(TypeAuction, source)

    def start_crawler(self):
        self.get_all_url()

    def get_detail(self, url_real, city_name, auction_type, html_type,auction_id,province,region):
        response = requests.get(url_real, headers=self.headers,verify=False)
        html = response.text
        if 'Status 500' in html or 'Error report' in html:
            log.info('请求错误，url="{}"'.format(url_real))
            return
        tree = etree.HTML(html)
        auction = Auction(source, auction_type)
        auction.html_type = html_type
        auction.province = province
        auction.city = city_name
        auction.region = region
        auction.source_html = html
        if auction_type == '住宅':
            self.house_detailparse(url_real, auction, tree,auction_id)
        else:
            self.other_parse(url_real, auction, tree,auction_id)

    @staticmethod
    def house_detailparse(url_real, auction, tree,auction_id):
        try:
            info = []
            auction.auction_name = tree.xpath('//div[@class="detail-info-title"]/p/text()')[0]
            city_info = tree.xpath('//div[@class="ct-story-box"]/span/a[2]')[0].tail
            start_auction_price = tree.xpath('//div[@class="detail-info-item fs14 cl3"]/em/a/text()')[0].strip()
            auction.start_auction_price = float(
                re.search('(\d+),?(\d+)', start_auction_price, re.S | re.M).group(1).replace(',', '')) * 10000
            auction_time = tree.xpath('//div[@class="detail-info-item fs14 cl3 relative"]/text()')[1]
            auction.auction_time = datetime.datetime.strptime(auction_time, "%Y-%m-%d\n")
            auction.build_type = tree.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[7]/div[1]/span/text()')[0]
            auction.area = tree.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[7]/div[2]/span/text()')[0]
            auction.court = tree.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[6]/text()')[1]
            info.append(tree.xpath('string(//div[@id="detail1"])'))
            auction.city = city_info.split('-')[0].split(' ')[-1]
            auction.region = city_info.split('-')[1].split('住宅拍卖')[0]
            auction.auction_id = auction_id
            auction.insert_db()
        except Exception as e:
            log.error('解析错误,url="{}",e="{}"'.format(url_real, e))

    @staticmethod
    def other_parse(url_real, auction, tree,auction_id):
        try:
            auction.auction_name = tree.xpath('//div[@class="detail_house_name"]/text()')[0]
            start_auction_price = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[1]/div[1]/em/text()')[0].strip()
            auction.start_auction_price = float(start_auction_price) * 10000
            auction.court = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[1]/div[5]/i/text()')[0]
            start_time = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[1]/div[2]/i/text()')[0]
            auction.start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
            auction.area = tree.xpath('/html/body/div/div[2]/div[2]/div[3]/div[2]/span/text()')[0]
            auction.assess_value = tree.xpath('//*[@id="information_one"]/div[2]/ul/li[5]/span/text()')[0].strip()
            auction.auction_id = auction_id
            auction.insert_db()
        except:
            log.error('解析错误,url={}'.format(url_real))

    def get_all_url(self):
        for i in self.city_code:
            city,region_id = i.code.split(',')
            city_name = i.city
            province = i.province
            region = i.region
            for type in self.map:
                url = 'https://' + city + '.51zhupai.com/' + type.code + '/' + region_id
                auction_type = type.auction_type
                html_type = type.html_type
                response = requests.get(url, headers=self.headers,verify=False)
                html = response.text
                tree = etree.HTML(html)
                page = tree.xpath('//a[@class="pageTotle"][4]/text()')[0]
                for p in range(1, int(page) + 1):
                    page_url = url + 'n' + str(p)
                    res = requests.get(page_url, headers=self.headers,verify=False)
                    html_ = res.text
                    tree_ = etree.HTML(html_)
                    url_list_ = tree_.xpath('//ul[contains(@class,"list_content_ul")]/li/a/@href')
                    for url_ in url_list_:
                        url_real = 'https://' + city + '.51zhupai.com' + url_
                        id_ = url_real.split('/')[-1]
                        is_exies = check_auction(source, id_)
                        if is_exies:
                            log.info('id已存在，id="{}"'.format(str(id_)))
                            continue
                        self.get_detail(url_real, city_name, auction_type, html_type,id_,province,region)
