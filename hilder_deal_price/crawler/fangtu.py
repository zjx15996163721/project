# from deal_price_info import Comm
from BaseClass import Base
import requests
import re
from lxml import etree
import time
import datetime
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
source = '房途网'
log = LogHandler('房途网')


class Fangtu(object):
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        self.start_url = 'http://hangzhou.fangtoo.com/building/'
        self.proxies = proxies

    def start_crawler(self):
        url = 'http://hangzhou.fangtoo.com/building/cp1/'
        res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        num = re.search('pagecount:(\d+),', res.text, re.S | re.M).group(1)

        for i in range(1, int(num)+1):
            url = self.start_url + "cp" + str(i) + "/"
            try:
                res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error("source={}, 请求失败 url={} e={}".format('房途网', url, e))
                continue
            self.parse(res)

    def parse(self, res):
        html = etree.HTML(res.text)
        comm_info_list = html.xpath("//li//div[@class='fang-info ml20 z']")
        for comm_info in comm_info_list:
            try:
                comm_url = comm_info.xpath("./div[@class='title']/a/@href")[0]
                region = comm_info.xpath(".//a[@class='ml20']/text()")[0]
                bu_id = re.search('\d+', comm_url).group(0)
                data = {
                    "buildingId": bu_id,
                    'pageIndex': 1,
                    'pageSize': 10000,
                }
            except Exception as e:
                log.error("解析失败,未找到小区名和区域, source={}, e={}".format('房途网', e))
                continue
            try:
                deal_res = requests.post('http://hangzhou.fangtoo.com/Building/GetTradeExchange/', data=data,
                                         headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error("请求失败 id={}, source={}, e={}".format('bu_id', '房途网', e))
                continue
            try:
                deal_dict = deal_res.json()
            except Exception as e:
                log.error("序列化失败 source={}, e={}".format('房途网', e))
                continue
            self.get_data(deal_dict, region)

    def get_data(self, deal_dict, region):
        for n in deal_dict['data']:
            co = Base(source)
            co.city = '杭州'
            try:
                size = n['Area']
                area = size.replace('㎡', '')
                area = float(area)
                co.area = round(area, 2)
            except:
                co.area = None
            try:
                co.district_name = n['Addr']
            except:
                co.district_name = None
            try:
                co.total_price = int(re.search('(\d+)', n['Price'], re.S | re.M).group(1))
            except:
                co.total_price = None
            try:
                co.avg_price = int(co.total_price / co.area)
            except:
                co.avg_price = None
            try:
                trade_date = n['ExDate']
                t = time.strptime(trade_date, "%Y/%m/%d %H:%M:%S")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                co.trade_date = co.local2utc(datetime.datetime(y, m, d))
            except:
                co.trade_dat = None
            co.region = region
            co.insert_db()
