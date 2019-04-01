"""
已经有id去重不请求详情页
"""
from lxml import etree
from auction import Auction, check_auction
from lib.mongo import Mongo
import yaml
import requests
import re
from lib.log import LogHandler
import datetime
from sql_mysql import TypeAuction,CityAuction,inquire

log = LogHandler(__name__)

source = 'chinesesfpm'  # 中国司法拍卖网

setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]


class ChineseFPM:
    def __init__(self):
        self.start_url = 'http://www.chinesesfpm.com/index/index/getAjaxSearch.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        self.data = {'court_sheng': None,
                     'court_city': None,
                     'court_arer': None,
                     'province': None,
                     'city': 0,
                     'min_price': None,
                     'max_price': None,
                     'do_paimai': 1,
                     'do_s_type': None,
                     'biaodi_type': 3,
                     'do_isajax': 1,
                     'page': 1,
                     'do_label': 0, }
        self.map = inquire(TypeAuction,'chinesesfpm')
        self.data_list = inquire(CityAuction, 'chinesesfpm')

    def start_crawler(self):
        self.category_fetch()

    def html_fetch(self,max_page,province_name,city_name,type_name,auction_type):
        if max_page is not None:
            for i in range(1, max_page+1):
                self.data['page'] = i
                res = requests.post(self.start_url, data=self.data, headers=self.headers)
                url_list = re.findall('index/index/info/biao_id/(.*?)"', res.text, re.S | re.M)
                for auction_id in url_list:
                    if not check_auction(source=source, auction_id=auction_id):
                        self.crawler_detail_page(auction_id,province_name, city_name,type_name,auction_type)
                    else:
                        log.info('数据库已经存在')

    def crawler_detail_page(self, auction_id,province_name, city_name, type_name,auction_type):
        detail_url = 'http://www.chinesesfpm.com/index/index/info/biao_id/' + auction_id
        res = requests.get(detail_url)
        tree = etree.HTML(res.text)
        a = Auction(source=source, auction_type=auction_type)
        a.auction_id = auction_id
        a.auction_name = tree.xpath('/html/body/div/div[6]/div/div[2]/div[1]/div[1]/text()')[0]
        a.html_type = type_name
        auction_time = tree.xpath('/html/body/div/div[6]/div/div[2]/div[1]/div[2]/div[2]/div[2]/text()')[0]
        auction_time_ = re.search('开始时间: (.*?)$', auction_time, re.S | re.M).group(1)
        a.auction_time = datetime.datetime.strptime(auction_time_, "%Y年%m月%d日  %H时%M分%S秒")
        a.province = province_name
        a.city = city_name
        a.info = [tree.xpath('string(//*[@id="f4"])'), tree.xpath('string(//*[@id="f6"])')]
        start_auction_price = \
            tree.xpath('/html/body/div/div[6]/div/div[2]/div[1]/div[2]/div[2]/div[5]/div[1]/em[3]/text()')[0]
        s = start_auction_price.encode('utf-8').decode()
        a.start_auction_price = float(re.search('起拍价: ￥(.*)', s, re.S | re.M).group(1))

        court = tree.xpath('/html/body/div/div[6]/div/div[2]/div[1]/div[2]/div[2]/div[5]/div[2]/em[1]/text()')[0]
        a.court = re.search('拍卖机构：(.*)', court, re.S | re.M).group(1)
        a.source_html = res.text
        a.insert_db()

    def get_all_page(self):
        res = requests.post(self.start_url, data=self.data, headers=self.headers)
        if '暂无数据' in res.text:
            log.info("暂无数据")
            return None
        else:
            try:
                max_page = max([i for i in re.findall('doAjaxSearch\((.*?)\)', res.text, re.S | re.M)])
            except:
                max_page = 1
            return int(max_page)

    def category_fetch(self):
        for n in range(1,4):
            do_paimai  = n
            self.data['do_paimai'] = do_paimai
            for location in self.data_list:
                province_name = location.province
                province_id = location.province_id
                for type in self.map:
                    type_id = type.code
                    type_name = type.html_type
                    auction_type = type.auction_type
                    self.data['province'] = int(province_id)
                    self.data['page'] = 1
                    self.data['biaodi_type'] = int(type_id)
                    self.data['city'] = 0
                    cate_res = requests.post(self.start_url,data=self.data,headers=self.headers)
                    if '暂无数据' in cate_res.text:
                        log.info('{}{}暂无数据'.format(province_name,type_name))
                        continue
                    else:
                        city_id = location.city_id
                        city_name = location.city
                        self.data['city'] = int(city_id)
                        max_page = self.get_all_page()
                        self.html_fetch(max_page,province_name,city_name,type_name,auction_type)




