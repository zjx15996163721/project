"""
已经有id去重不请求详情页
"""
import requests
from auction import Auction
from lib.log import LogHandler
from lib.mongo import Mongo
from lxml import etree
import datetime
import yaml
import re
import math
from sql_mysql import inquire, TypeAuction

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port'], ).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = 'jingdong'
log = LogHandler(__name__)
type_list = inquire(TypeAuction, source)
s = requests.session()


class Jingdong(object):
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        }
        self.count = 0

    def start_crawler(self):
        for type_num in type_list:
            if type_num.code == '13809' or type_num.code == '13810' or type_num.code == '13817' or type_num.code == '12728':
                page_num = self.get_page(type_num.code)
                for page in range(1, int(page_num) + 1):
                    url = 'http://auction.jd.com/getJudicatureList.html?page=' + str(
                        page) + '&limit=40&provinceId=2&childrenCateId=' + type_num.code
                    try:
                        response = s.get(url=url, headers=self.headers)
                        html = response.json()
                        try:
                            for info in html['ls']:
                                auction = Auction(source=source)
                                auction.name = info['title']  # 商品名
                                auction.evalPrice = float(int(info['assessmentPrice'])/10000)  # 评估值
                                auction.city = info['province']  # 省（上海）
                                auction.region = info['city']  # 城市（区域）
                                auction.curPrice = float(int(info['currentPrice'])/10000)    # 当前价格
                                auction.endShootingDate = datetime.datetime.fromtimestamp(int(info['endTime']) / 1000)      #  结束时间
                                auction.startShootingDate = datetime.datetime.fromtimestamp(int(info['startTime']) / 1000)  #  开始时间
                                auction.auction_id = str(info['id'])  # 商品id
                                is_exist = coll.find_one({'auction_id': str(info['id']), 'source': source})
                                if is_exist:
                                    log.info('id已存在，id="{}"'.format(str(info['id'])))
                                    continue
                                try:
                                    self.get_detail(str(info['id']), auction)
                                except Exception as e:
                                    log.error('这条数据没有起拍价，为变卖价')
                        except Exception as e:
                            log.error('解析错误，url="{}"'.format(url))
                    except Exception as e:
                        log.error('请求错误，url="{}"'.format(url))

    def get_detail(self, id_, auction):
        detail_url = 'http://paimai.jd.com/' + str(id_)
        response = s.get(url=detail_url, headers=self.headers)
        tree = etree.HTML(response.text)
        html = response.text
        startPrice = re.search('起拍价：.*?<em.*?>&yen;(.*?)</em>', html, re.S | re.M).group(1)     # 起拍价
        auction.startPrice = float(int(startPrice.replace(' ', '').replace(',', ''))/10000)
        bond = re.search('保证金：.*?<span.*?>&yen;(.*?)</span>', html, re.S | re.M).group(1)       # 保证金
        auction.bond = float(int(bond)/10000)
        auctionStage_info = tree.xpath('//div[@id="content"]/div[1]/div[2]/div[1]/div[1]/div[2]/h1/text()')[0]
        auctionStage_info = auctionStage_info.replace(' ', '').replace('\n', '').replace('\t', '')
        auctionStage = auctionStage_info.split('】')[0].split('【')[1]                              # 拍卖阶段
        auction.auctionStage = auctionStage
        skulid = re.search('id="skuId" value="(.*?)"', html, re.S | re.M).group(1)
        auction.dealPrice = self.get_deal(skulid, id_)                                              # 成交价
        auction.address = self.get_address(id_)                                                     # 地址
        tree = etree.HTML(html)
        auction.insert_db()

    def get_deal(self, skulid, id_):
        url = 'http://paimai.jd.com/json/current/englishquery.html?paimaiId={}&skuId={}&start=0&end=9'.format(id_, skulid)
        res = requests.get(url=url, headers=self.headers)
        if res.json()['auctionStatus'] == '2':  # 状态为2 表示成交
            return res.json()['currentPrice']
        else:
            return None

    def get_address(self, id_):
        address_url = 'http://mpaimai.jd.com/json/mobile/getProductbasicInfo.html?paimaiId=' + str(id_)
        headers = {
            'Referer': "http://mpaimai.jd.com/json/mobile/toProductLocation.html?paimaiId=" + str(id_),
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        }
        response = s.get(url=address_url, headers=headers, allow_redirects=False)
        html = response.json()
        try:
            address = html['productAddress']['address']
        except Exception as e:
            address = None
        return address

    def get_page(self, type_num):
        url_page = 'http://auction.jd.com/getJudicatureList.html?page=1&limit=40&provinceId=2&childrenCateId=' + str(
            type_num)
        response = s.get(url=url_page, headers=self.headers)
        number = response.json()['total']
        page = math.ceil(int(number) / 40)
        return page
