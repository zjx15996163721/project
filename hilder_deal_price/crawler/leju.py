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
source = '新浪乐居'
log = LogHandler('新浪乐居')


class Leju(object):

    def __init__(self, proxies):
        self.start_url = 'https://esf.leju.com/city/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        self.proxies = proxies

    def start_crawler(self):
        res = requests.get(self.start_url, headers=self.headers, proxies=self.proxies)
        html = etree.HTML(res.text)
        city_list = html.xpath("//dl//dd/a")
        for i in city_list:
            city_url = i.xpath("./@href")[0]
            city_name = i.xpath("./@title")[0]
            if 'house' in city_url:
                second_comm_url = city_url.replace('house', 'community')
            else:
                second_comm_url = city_url + '/community/'
            self.community(second_comm_url, city_name)

    def community(self, second_comm_url, city_name):
        count = 1
        while True:
            page_url = second_comm_url + "n" + str(count) + "/"
            try:
                res = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求错误,source="{}"，url="{}",e="{}"'.format('新浪乐居', page_url, e))
                count += 1
                continue
            if '没有符合条件的结果' in res.text:
                log.info('source="{}", 无二手小区'.format('新浪乐居'))
                break
            else:
                co_html = etree.HTML(res.text)
                co_list = co_html.xpath("//div[@class='right-information']")
                count += 1
            self.room(co_list, city_name)

    def room(self, co_list, city_name):
        for co in co_list:
            try:
                co_name = co.xpath("./div[1]/a/text()")[0]
                co_url = "http:" + co.xpath("./div[1]/a/@href")[0]
                region = co.xpath("./div[3]/span[1]/a[1]/text()")[0]
            except:
                continue
            try:
                detail = requests.get(url=co_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求错误,source="{}"，url="{}",e="{}"'.format('新浪乐居', co_url, e))
                continue
            html = etree.HTML(detail.text)
            try:
                room_url = "http:" + html.xpath("//div[@class='tab-toolbar pr']//li/a/@href")[-1]
            except Exception as e:
                log.error('无成交数据, source="{}",e="{}"'.format('新浪乐居', e))
                continue
            self.parse(room_url, co_name, region, city_name)

    def parse(self, room_url, co_name, region, city_name):
        try:
            page_index = requests.get(url=room_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求错误, source="{}"，url="{}",e="{}"'.format('新浪乐居', room_url, e))
            return
        if re.search('共(\d+)页', page_index.text):
            page_num = re.search('共(\d+)页', page_index.text).group(1)
            for i in range(1, int(page_num) + 1):
                url = re.sub('#.*', 'n', room_url) + str(i)
                while True:
                    try:
                        res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
                        break
                    except Exception as e:
                        log.error('请求错误, source="{}"，url="{}",e="{}"'.format('新浪乐居', url, e))
                        continue
                con = res.text
                room_html = etree.HTML(con)
                room_list = room_html.xpath("//div[@class='right-information']")
                for m in room_list:
                    room = Base(source)
                    room.url = url
                    # 小区名
                    room.district_name = co_name
                    # 城市
                    room.city = city_name
                    # 区域
                    room.region = region
                    room_type = m.xpath("./h3/span[2]/text()")[0]
                    try:
                        # 室
                        room.room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
                    except:
                        room.room = None
                    try:
                        # 厅
                        room.hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
                    except:
                        room.hall = None
                    # 面积
                    size = m.xpath("./h3/span[3]/text()")[0]
                    area = size.replace('平米', '')
                    if area:
                        area = float(area)
                        room.area = round(area, 2)
                    # 总价
                    # total_price = m.xpath(".//div[@class='price fs14 ']/em/text()")[0]
                    # room.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1))*10000
                    # 均价
                    avg_price = m.xpath(".//div[@class='size  fs14']/text()")[0]
                    room.avg_price = int(re.search('(\d+)', avg_price, re.S | re.M).group(1))
                    try:
                        room.total_price = int(int(room.avg_price)*float(room.area))
                    except:
                        room.total_price = None
                    try:
                        fitment_direction_info = m.xpath(".//div[@class='t1 fs14']")[0]
                        fitment_direction_info = fitment_direction_info.xpath('string(.)')
                        fitment_direction_info = fitment_direction_info.split('|')
                        if len(fitment_direction_info) == 2:
                            room.fitment = fitment_direction_info[1]
                            room.direction = fitment_direction_info[0]
                        elif len(fitment_direction_info) == 3:
                            room.fitment = fitment_direction_info[2]
                            room.direction = fitment_direction_info[1]
                    except:
                        room.fitment = None
                        room.direction = None

                    floor_info = m.xpath(".//div[@class='fs14']/text()[1]")[0]
                    try:
                        floor = re.search('(.*?)/', floor_info).group(1)
                        room.floor = int(re.search('\d+', floor).group(0))
                    except Exception as e:
                        room.floor = None
                    try:
                        room.height = int(re.search('.*?/(\d+)层', floor_info).group(1))
                    except:
                        room.height = None
                    trade_date = m.xpath(".//div[@class='date']/text()")[0]
                    if trade_date:
                        t = time.strptime(trade_date, "%Y-%m-%d")
                        y = t.tm_year
                        m = t.tm_mon
                        d = t.tm_mday
                        room.trade_date = room.local2utc(datetime.datetime(y, m, d))
                    room.insert_db()
        else:
            log.info('source={}, url={}, 小区无相关数据'.format('新浪乐居', room_url))
            return

