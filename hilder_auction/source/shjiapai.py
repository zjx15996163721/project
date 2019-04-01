"""
已经有id去重不请求详情页
"""
import requests
from auction import Auction,check_auction
from lib.log import LogHandler
from lib.mongo import Mongo
from lxml import etree
import yaml
import re

setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]
log = LogHandler(__name__)
source = 'shjiapai'
auction_type = '住宅'

class Shjiapai:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
    def start_crawler(self,i=1):
        url = 'http://www.shjiapai.cn/Fyzs/index/p/' + str(i) + '.html'
        index_res = requests.get(url,headers=self.headers)
        content = index_res.content.decode()
        html = etree.HTML(content)
        self.parse(html)
        if '下一页' in content:
            i+=1
            return self.start_crawler(i)

    def parse(self,html):
        auction_list = html.xpath("//dl/dd/a/@href")
        for auction_url in auction_list:
            try:
                url = 'http://www.shjiapai.cn'+auction_url
                auction_res = requests.get(url,headers=self.headers)
                con = auction_res.text
                auction_id = re.search('id/(\d+).html', auction_url).group(1)
                if not check_auction(source=source, auction_id=auction_id):
                    auction = Auction(source=source, auction_type=auction_type)
                    auction.source_html = con
                    auction.auction_id = auction_id
                    auction.auction_name = re.search('楼盘名称.*?">(.*?)</td',con,re.S|re.M).group(1)
                    auction.city = '上海'
                    auction.html_type = '房产'
                    auction.start_auction_price = re.search('预计售价.*?">(.*?)</td',con,re.S|re.M).group(1)
                    auction.floor = re.search('层.*?">(.*?)楼</td',con,re.S|re.M).group(1)
                    auction.area = re.search('户型面积.*?">(.*?)</td',con,re.S|re.M).group(1)
                    auction.build_type = re.search('物业类型.*?">(.*?)</td',con,re.S|re.M).group(1)
                    auction.info = re.search('其它.*?>(.*?)</div',con,re.S|re.M).group(1)
                    auction.insert_db()
                else:
                    log.info("数据已存在")
            except Exception as e:
                log.error("{}解析失败".format(auction_url))






