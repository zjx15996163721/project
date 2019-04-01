"""
青岛市拍卖中心
已经有id去重不请求详情页
"""
import requests
from lxml import etree
from auction import Auction
import datetime
import re
import yaml
from lib.mongo import Mongo
from lib.log import LogHandler


setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = '青岛市拍卖中心'
auction_type = '其他'
log = LogHandler(__name__)


class Qingdaopaimai(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        self.start_url = 'http://auction.qdauction.com/items'

    # 获取最大页码
    def get_page_num(self):
        response = requests.get(url=self.start_url, headers=self.headers)
        html = etree.HTML(response.text)
        page = html.xpath('/html/body/div/div[3]/nav/span[8]/a/@href')[0]
        max_num = re.search('/items\?page=(\d+)', page).group(1)
        print(max_num)
        return int(max_num)

    # 获取所有的列表页链接
    def get_page_links(self, max_num):
        page_links = []
        for page_num in range(max_num):
            url = (self.start_url + '?page={}').format(page_num+1)
            print(url)
            page_links.append(url)
        return page_links

    # 获取所有的详情页链接
    def get_details_links(self, url):
        details_links = []
        response = requests.get(url=url, headers=self.headers)
        html = etree.HTML(response.text)
        links = html.xpath('/html/body/div/div[3]/div/div/div[2]/div/a/@href')
        for link_id in links:
            link = 'http://auction.qdauction.com' + link_id
            print(link)
            auction_id = re.search("/items/(\d+)", link_id).group(1)
            is_exist = coll.find_one({'source': source, 'auction_id': str(auction_id)})
            if is_exist:
                log.info('id已存在，id="{}"'.format(str(auction_id)))
                continue
            details_links.append(link)
        return details_links

    # 调用入口
    def start_crawler(self):
        max_page = self.get_page_num()
        page_links = self.get_page_links(max_page)
        for page_link in page_links:
            detail_links = self.get_details_links(page_link)
            for detail_url in detail_links:
                self.get_info(detail_url)

    # 获取详情页字段
    def get_info(self, url):
        response = requests.get(url=url, headers=self.headers)
        html = etree.HTML(response.text)
        print(url)
        wrong_list = []
        try:
            wrong = html.xpath("//div[@class='dialog']/h1/text()")[0]
            wrong_list.append(wrong)
        except Exception as e:
            print(e)
        if "We're sorry, but something went wrong." not in wrong_list:
            title = html.xpath("//div[@class='title']/text()")[0]
            start_price = html.xpath("//table[@class='item-attrs']//tr[1]/td[2]/text()")[0]
            assess_price = html.xpath("//table[@class='item-attrs']//tr[1]/td[4]/text()")[0]
            ensure_price = html.xpath("//table[@class='item-attrs']//tr[1]/td[6]/text()")[0]
            auction_id = re.search("http://auction\.qdauction\.com/items/(\d+)", url).group(1)
            auction = Auction(source=source, auction_type=auction_type)
            auction.auction_name = title
            auction.start_auction_price = start_price
            auction.assess_value = assess_price
            auction.earnest_money = ensure_price
            auction.auction_id = auction_id
            try:
                time = html.xpath("//tr[@class='deal']/td[4]/text()")[0]
                Auction.auction_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(e)
            auction.source_html = response.text
            auction.city = '青岛'
            auction.html_type = '其他'
            auction.insert_db()

