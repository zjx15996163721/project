"""
已经有id去重不请求详情页
"""
import requests
import datetime
import yaml
from auction import Auction,check_auction
from lib.log import LogHandler
from lib.mongo import Mongo
from sql_mysql import TypeAuction,inquire

setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]
log = LogHandler(__name__)
source = 'laipaiya'

class Laipaiya:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.map = inquire(TypeAuction,source)

    def start_crawler(self):
        for cate in self.map:
            auction_type = cate.auction_type
            html_type = cate.html_type
            temp = "http://api.faepai.com/index.php/Web/InterfaceV2/searchObject?grabtype="+cate.code+"&page="
            self.page_turning(auction_type,html_type,temp,page=1)

    def page_turning(self,auction_type,html_type,temp,page):
        while True:
            page_url = temp + str(page)
            log.info('{}第{}页开始'.format(html_type,page))
            res = requests.get(page_url,headers=self.headers)
            if not res.json()['object']:
                break
            else:
                self.id_check(auction_type,html_type,res)
            page += 1

    def id_check(self,auction_type,html_type,res):
        for i in res.json()['object']:
            try:
                auction_id = i['djlsh']
                auction_url = 'http://api.faepai.com/index.php/Web/InterfaceV2/getObjectDetail?object_id='+str(auction_id)
                try:
                    auction_res = requests.get(auction_url,headers=self.headers)
                except:
                    log.error("{}请求失败".format(auction_url))
                    continue
                if not check_auction(source=source, auction_id=auction_id):
                    self.detail_parse(auction_res,auction_type,html_type,auction_id)
                else:
                    log.info("数据已存在")
            except Exception as e:
                log.error("解析失败{}".format(e))

    @staticmethod
    def detail_parse(auction_res,auction_type,html_type,auction_id):
        con = auction_res.json()
        auction = Auction(source=source,auction_type=auction_type)
        auction.source_html = con
        auction.html_type = html_type
        auction.auction_id = auction_id
        auction.auction_name = con['object_title']
        auction.start_auction_price = con['start_price']
        auction.assess_value = con['appraise_price']
        auction.earnest_money = con['bond_price']
        auction.court = con['court_name']
        auction_time = con['start_time']
        location = con['location']
        auction.auction_time = datetime.datetime.strptime(auction_time, "%Y-%m-%d %H:%M:%S")
        province,city,region = location.split(' ')
        auction.province = province
        auction.city = city
        auction.region = region
        if html_type == '房产':
            auction.floor = con['detail']['house_floor']
            auction.area = con['detail']['gross_floor_area']
        elif html_type == '土地':
            auction.area = con['detail']['l_land_area']
        auction.insert_db()



