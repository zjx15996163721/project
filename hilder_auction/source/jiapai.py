"""
已经有id去重不请求详情页
"""
import yaml
import requests
from lib.log import LogHandler
from lib.mongo import Mongo
from lxml import etree
from sql_mysql import inquire, TypeAuction
from auction import Auction
import re
import datetime

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = 'jiapai'
log = LogHandler(__name__)


class Jiapai:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.list_info = []
        self.type_list = inquire(TypeAuction, source)

    def start_crawler(self):
        for type_ in self.type_list:
            html_type = type_.html_type
            auction_type = type_.auction_type
            url = 'http://www.jiapai.net.cn/index.php/Judicial/index/px/' + type_.code
            response = requests.get(url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            page_url = tree.xpath('//a[@class="end"]/@href')[0]
            page = re.search('p/(\d+).html', page_url, re.S | re.M).group(1)
            for i in range(1, int(page) + 1):
                url_page = 'http://www.jiapai.net.cn/index.php/Judicial/index/px/109/p/' + str(i) + '.html'
                self.get_list_info(url_page, html_type, auction_type)

    def get_list_info(self, url_page, html_type, auction_type):
        response = requests.get(url_page, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        div_list = tree.xpath('//div[@class="sflistdiv"]')
        for i in div_list:
            info = []
            auction = Auction(source, auction_type)
            auction.province = '上海'
            auction.city = '上海'
            auction.html_type = html_type
            auction.source_html = html
            auction_id = i.xpath('div[@class="sflistdivn2"]/div[@class="f20hei"]/a/@href')[0].split('/')[-1]
            is_exist = coll.find_one({'auction_id': str(auction_id), 'source': source})
            if is_exist:
                log.info('id已存在，id="{}"'.format(str(auction_id)))
                continue
            auction.auction_id = auction_id
            try:
                auction_name_ = i.xpath('div[@class="sflistdivn2"]/div[@class="f20hei"]/a/text()')[0]
            except Exception as e:
                auction_name_ = ''
            region = i.xpath('div[@class="sflistdivn2"]/div[@class="sflistban"]/text()')[0]
            auction.region = re.search(' - (.*?)$', region, re.S | re.M).group(1)
            auction_time_ = i.xpath('div[@class="sflistdivn2"]/div[@class="sflisttime"]/text()')[0]
            address = i.xpath('div[@class="sflistdivn2"]/div[@class="sflistcan"]/text()')[3].encode().decode()
            auction.auction_name = auction_name_ + address
            try:
                auction_time = re.search('拍卖时间：(.*?)$', auction_time_, re.S | re.M).group(1)
                auction.auction_time = datetime.datetime.strptime(auction_time, "%y.%m.%d")
            except Exception as e:
                auction.auction_time = None
            info.append(i.xpath('string(div[@class="sflistdivn2"])'))
            area_ = i.xpath('div[@class="sflistdivn2"]/div[@class="sflistcan"]/span[1]/text()')[0]
            auction.area = re.search('面积：(.*?)$', area_, re.S | re.M).group(1)
            floor = i.xpath('div[@class="sflistdivn2"]/div[@class="sflistcan"]/span[3]/text()')[0]
            auction.floor = re.search('楼层：(.*?)$', floor, re.S | re.M).group(1)
            start_auction_price = i.xpath('//div[@class="f34hong"]/text()')[0]
            auction.start_auction_price = float(
                re.search('(\d+),?(\d+)', start_auction_price, re.S | re.M).group(1).replace(',', '')) * 10000
            auction.insert_db()
