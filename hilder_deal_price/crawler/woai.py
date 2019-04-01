# from deal_price_info import Comm
from BaseClass import Base
import requests
import re
from lxml import etree
import time
import datetime
from lib.log import LogHandler

source = '我爱我家'
log = LogHandler('我爱我家')


class Woai(object):

    def __init__(self, proxies):
        self.start_url = 'https://sh.5i5j.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.proxies = proxies

    def start_crawler(self):
        res = requests.get(url=self.start_url, headers=self.headers, proxies=self.proxies)
        html = etree.HTML(res.text)
        city_list = html.xpath("//p[@class='city fl']/a")
        for city in city_list:
            city_name = city.xpath("./text()")[0]
            city_url = city.xpath("./@href")[0]
            i = 1
            self.comm_info(city_url, city_name, i)

    def comm_info(self, city_url, city_name, i):
        url = city_url + 'xiaoqu/n' + str(i) + '/_?zn='
        try:
            co_res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败，source="{}",url="{}",e="{}"'.format('我爱我家', url, e))
            return
        html = etree.HTML(co_res.text)
        co_list = html.xpath("//div[@class='listCon']")
        for co in co_list:
            try:
                # 小区名
                co_name = co.xpath("./h3/a/text()")[0]
                co_url = co.xpath("./h3/a/@href")[0]
                # 区域
                region = co.xpath("./div[@class='listX']/p[3]/text()")[1]
                if '·' in region:
                    region = region.split('·')[0]
                else:
                    region = region
                co_id = re.search('\d+', co_url).group(0)
                sold_url = city_url + 'sold/' + str(co_id)
            except Exception as e:
                log.error('解析错误，source="{}",url="{}",e="{}"'.format('我爱我家', url, e))
                continue
            self.room_info(sold_url, co_name, region, city_name, city_url)
        if '下一页' in co_res.text:
            i += 1
            return self.comm_info(city_url, city_name, i)
        else:
            return

    def room_info(self, sold_url, co_name, region, city_name, city_url):
        try:
            room_res = requests.get(url=sold_url, headers=self.headers, proxies=self.proxies)
            ro_html = etree.HTML(room_res.text)
        except Exception as e:
            log.error('请求失败 source={}, url={} e={}'.format('我爱我家', sold_url, e))
            return
        try:
            self.info_parse(ro_html, co_name, region, city_name)
            self.page_request(room_res, ro_html, city_url, co_name, region, city_name)
        except Exception as e:
            log.info('source={}, 无二手成交信息{}'.format('我爱我家', e))

    def info_parse(self, ro_html, co_name, region, city_name):
        room_list = ro_html.xpath("//ul[@class='pList zu']/li")
        for room in room_list:
            ro = Base(source)
            # 城市
            ro.city = city_name
            # 小区名
            ro.district_name = co_name
            # 区域
            ro.region = region
            room_type = room.xpath(".//p[@class='sTit']/strong/text()")[0]
            try:
                # 室
                ro.room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
            except Exception as e:
                ro.room = None
            try:
                # 厅
                ro.hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
            except Exception as e:
                ro.hall = None
            try:
                # 卫数
                ro.toilet = int(re.search('(\d)卫', room_type, re.S | re.M).group(1))
            except Exception as e:
                ro.toilet = None
            # # 总价
            # total_price = room.xpath(".//div[@class='jiage']/strong/text()")[0]
            # ro.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
            # 均价
            avg_price = room.xpath(".//div[@class='jiage']/p/text()")[0]
            ro.avg_price = int(re.search('(\d+)', avg_price, re.S | re.M).group(1))
            # 面积
            info = room.xpath(".//div/p[2]/text()")[0]
            area = re.search('·(.*?)平米', info).group(1)
            area = float(area)
            ro.area = round(area, 2)
            try:
                ro.total_price = int(int(ro.avg_price)*float(ro.area))
            except:
                ro.total_price = None
            # 朝向
            direction = re.search('平米 · (.*)', info).group(1)
            ro.direction = direction.strip()
            # 交易日期
            trade_date = room.xpath(".//div/p[3]/text()")[0]
            trade_date = trade_date.strip()
            t = time.strptime(trade_date, "成交日期：%Y-%m-%d")
            y = t.tm_year
            m = t.tm_mon
            d = t.tm_mday
            ro.trade_date = ro.local2utc(datetime.datetime(y, m, d))
            ro.insert_db()

    def page_request(self, res, ro_html, city_url, co_name, region, city_name):
        if '下一页' in res.text:
            url = city_url[:-1] + ro_html.xpath("//a[@class='cPage']/@href")[0]
            log.info('source={}, 开始抓取下一页'.format('我爱我家'))
            try:
                res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败 source={}, url={} e={}'.format('我爱我家', url, e))
                return
            ro_html = etree.HTML(res.text)
            self.info_parse(ro_html, co_name, region, city_name)
            return self.page_request(res, ro_html, city_url, co_name, region, city_name)
        else:
            log.info('source={}, 没有下一页'.format('我爱我家'))
            return
