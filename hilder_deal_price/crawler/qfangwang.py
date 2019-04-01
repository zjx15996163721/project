import requests
import re
from lxml import etree
# from deal_price_info import Comm
from BaseClass import Base
import time
import datetime
from lib.log import LogHandler

log = LogHandler('Q房网')
url = 'https://dongguan.qfang.com/'


class Qfangwang(object):

    def __init__(self, proxies, cookie):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'cookie': cookie
        }
        self.proxies = proxies

    def start_crawler(self):
        response = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        html = response.text
        info_html = re.search('cities-opts clearfix"(.*?)end cities', html, re.S | re.M).group(1)
        city_str_list = re.findall('<a.*?</a>', info_html, re.S | re.M)
        for city_str in city_str_list:
            city_url_head = re.search('href="(.*?)"', city_str, re.S | re.M).group(1)
            city_url = 'https:' + city_url_head + '/transaction'
            city = re.search('<a.*?>(.*?)<', city_str, re.S | re.M).group(1)
            self.get_city_info(city_url, city)

    def get_city_info(self, city_url, city):
        try:
            response = requests.get(url=city_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求错误，url="{}", source={},e="{}"'.format(city_url, 'Q房网', e))
            return
        html = response.text
        try:
            area_str = re.search('class="search-area-detail clearfix".*?</ul>', html, re.S | re.M).group()
        except Exception as e:
            log.error('获取区域信息失败，url="{}", source={},e="{}"'.format(city_url, 'Q房网', e))
            return
        area_info_list = re.findall('<a.*?</a>', area_str, re.S | re.M)[1:]
        for i in area_info_list:
            area_url_head = re.search('href="(.*?)"', i, re.S | re.M).group(1)
            # 区域
            area = re.search('<a.*?>(.*?)<', i, re.S | re.M).group(1)
            area_url = city_url.replace('/transaction', '') + area_url_head
            print(area_url)
            try:
                result = requests.get(url=area_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败，source="{}",url="{}",e="{}"'.format('Q房网', area_url, e))
                continue
            content = result.text
            try:
                page_html = re.search('class="turnpage_num".*?</p>', content, re.S | re.M).group()
                page = re.findall('<a.*?>(.*?)<', page_html, re.S | re.M)[-1]
            except Exception as e:
                log.error('获取页码失败，source="{}",url="{}",e="{}"'.format('Q房网', area_url, e))
                continue
            for i in range(1, int(page) + 1):
                page_url = area_url + '/f' + str(i)
                self.get_page_url(page_url, city, area)

    def get_page_url(self, page_url, city, region):
        try:
            response = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败，source="{}",url="{}",e="{}"'.format('Q房网', page_url, e))
            return
        self.get_detail(response, city, region, page_url)

    def get_detail(self, response, city, region, url):
        html = response.text
        tree = etree.HTML(html)
        info_list = tree.xpath("//div[@class='house-detail']/ul/li")
        for info in info_list:
            comm = Base('Q房网')
            # 链接
            comm.url = url
            # 城市
            comm.city = city.strip()
            # 区域
            comm.region = region.strip()
            district_name_room_area = info.xpath("./div[1]/p[1]/a[1]/text()")[0]
            # 小区名称
            comm.district_name = district_name_room_area.split(' ')[0]
            # 室
            try:
                comm.room = int(re.search("(\d+)室", district_name_room_area, re.S | re.M).group(1))
            except:
                comm.room = None
            # 厅
            try:
                comm.hall = int(re.search("(\d+)厅", district_name_room_area, re.S | re.M).group(1))
            except:
                comm.hall = None
            # 面积
            try:
                area = re.search("(\d+.?\d+?)平米", district_name_room_area, re.S | re.M).group(1)
                comm.area = round(float(area), 2)
            except:
                comm.area = None
            # 朝向 总楼层
            try:
                direction = info.xpath("./div[1]/p[2]/span[4]/text()")[0]
                if '层' not in direction:
                    comm.direction = direction
                    height = info.xpath("./div[1]/p[2]/span[6]/text()")[0]
                    comm.height = int(re.search("(\d+)层", height, re.S | re.M).group(1))
                else:
                    comm.direction = None
                    comm.height = int(re.search("(\d+)层", direction, re.S | re.M).group(1))
            except:
                comm.direction = None
                comm.height = None
            # # 总价
            # try:
            #     total_price = info.xpath("./div[2]/span[1]/text()")[0]
            #     comm.total_price = int(total_price) * 10000
            # except:
            #     comm.total_price = None
            # 均价
            try:
                avg_price = info.xpath("./div[2]/p[1]/text()")[0]
                comm.avg_price = int(re.search("\d+", avg_price, re.S | re.M).group(0))
            except:
                comm.avg_price = None
            # 总价
            try:
                comm.total_price = int(int(comm.avg_price)*float(comm.area))
            except:
                comm.total_price = None
            # 交易时间
            try:
                trade_date = info.xpath("./div[3]/span[1]/text()")[0]
                t = time.strptime(trade_date, "%Y.%m.%d")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                comm.trade_date = comm.local2utc(datetime.datetime(y, m, d))
            except:
                comm.trade_date = None
            comm.insert_db()

