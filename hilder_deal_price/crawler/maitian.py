import requests
from lxml import etree
# from deal_price_info import Comm
from BaseClass import Base
import re
import time
import datetime
from lib.log import LogHandler
source = '麦田'
log = LogHandler('麦田')


class Maitian(object):

    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.url = 'http://bj.maitian.cn/xqall'
        self.proxies = proxies

    def start_crawler(self):
        res = requests.get(url=self.url, headers=self.headers, proxies=self.proxies)
        html = etree.HTML(res.text)
        city_list = html.xpath("//div[@class='filter_select clearfix selectBox']//li/a/@href")
        for city in city_list:
            city_url = city + "/xqall"
            self.crawler(city_url, city)

    def crawler(self, city_url, city):
        print(city_url)
        try:
            res = requests.get(url=city_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求错误，source="{}",url="{}",e="{}"'.format('麦田', city_url, e))
            return
        con = etree.HTML(res.text)
        try:
            last_page = con.xpath("//a[@class='down_page']/@href")[1]
            page_num = re.search('\d+', last_page).group(0)
        except Exception as e:
            log.error('获取页码失败，source="{}",url="{}",e="{}"'.format('麦田', city_url, e))
            return
        for i in range(1, int(page_num) + 1):
            page_url = city_url + "/PG" + str(i)
            try:
                page_res = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求错误，source="{}",url="{}",e="{}"'.format('麦田', page_url, e))
                continue
            page_con = etree.HTML(page_res.text)
            temp = page_con.xpath("//h1/a/@href")
            for temp_url in temp:
                com = Base(source)
                comm_url = city + temp_url
                com.url = comm_url
                try:
                    co_res = requests.get(url=comm_url, headers=self.headers, proxies=self.proxies)
                except Exception as e:
                    log.error('请求错误，source="{}",url="{}",e="{}"'.format('麦田', comm_url, e))
                    continue

                co_con = etree.HTML(co_res.text)
                # 城市
                try:
                    com.city = co_con.xpath("//div/a[@class='show']/text()")[0]
                    # 区域
                    region = co_con.xpath("//section[@class='fl home_main']/p[3]/a/text()")[-1]
                    com.region = re.search("\[(.*)\]", region, re.S | re.M).group(1)
                    # 小区名称
                    com.district_name = co_con.xpath("//cite/span/text()")[0]
                    info = co_con.xpath("//table/tbody/tr")
                except Exception as e:
                    log.error('获取城市区域小区名失败, source="{}",url="{}",e="{}"'.format('麦田', comm_url, e))
                    continue
                for tag in info:
                    size = tag.xpath("./td[2]/text()")[0]
                    area = size.replace('㎡', '')
                    area = float(area)
                    # 面积
                    com.area = round(area, 2)
                    # 均价
                    avg_price = tag.xpath("./td[3]/text()")[0]
                    com.avg_price = int(re.search('(\d+)', avg_price, re.S | re.M).group(1))
                    # # 总价
                    # total_price = tag.xpath("./td/span/text()")[0]
                    # com.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
                    try:
                        com.total_price = int(int(com.avg_price)*float(com.area))
                    except:
                        com.total_price = None
                    # 成交日期
                    trade_date = tag.xpath("./td/text()")[-2]
                    if trade_date:
                        t = time.strptime(trade_date, "%Y-%m-%d")
                        y = t.tm_year
                        m = t.tm_mon
                        d = t.tm_mday
                        com.trade_date = com.local2utc(datetime.datetime(y, m, d))
                    room_type = tag.xpath("./td//p/a/text()")[0]
                    try:
                        # 室
                        com.room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
                    except:
                        com.room = None
                    try:
                        # 厅
                        com.hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
                    except:
                        com.hall = None
                    # 总楼层
                    floor = tag.xpath("./td//p/span/text()")[0]
                    com.floor = int(re.search('(\d+)层', floor, re.S | re.M).group(1))
                    # 朝向
                    com.direction = floor.split(' ')[1]
                    com.insert_db()

