"""
已经有id去重不请求详情页
"""
import requests
from auction import Auction
from sql_mysql import inquire, TypeAuction
from lib.log import LogHandler
from lib.mongo import Mongo
from lxml import etree
import datetime
import yaml
import re

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]

source = 'ali'
log = LogHandler(__name__)
s = requests.session()


class Ali:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                            (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.type_list = inquire(TypeAuction, source)

    def start_crawler(self):
        url = 'https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.13.pwypBc&city=&province=&\
                auction_start_seg=-1'
        try:
            response = s.get(url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            province_list = tree.xpath('//li[@class="triggle"]/em/a')  # 获取所有省
            for province in province_list:
                province_url = 'http:' + province.xpath('@href')[0].replace('\t', '').replace(' ', '')
                province_name = province.xpath('text()')[0]
                self.get_city_info(province_url, province_name)
        except Exception as e:
            log.error('起始页页请求错误，url="{}",e="{}"'.format(url, e))

    def get_city_info(self, province_url, province_name):
        # 获取所有城市
        try:
            response = s.get(province_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            city_list = tree.xpath('//div[contains(@class,"sub-condition J_SubCondition")]/ul/li/em/a')
            for city in city_list:
                city_url = 'http:' + city.xpath('@href')[0].replace('\t', '').replace(' ', '')
                city_name = city.xpath('text()')[0]
                self.get_region_info(city_url, city_name, province_name)
        except Exception as e:
            log.error('城市页请求错误，url="{}",e="{}"'.format(province_url, e))

    def get_region_info(self, city_url, city_name, province_name):
        # 获取所有区域
        try:
            response = s.get(city_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            region_list = tree.xpath('//div[contains(@class,"small-subcondion")]/ul/li/em/a')
            for region in region_list:
                region_url = 'http:' + region.xpath('@href')[0].replace('\t', '').replace(' ', '')
                region_name = region.xpath('text()')[0]
                self.add_all_type(region_url, region_name, city_name, province_name)
        except Exception as e:
            log.error('区域页请求错误，url="{}",e="{}"'.format(city_url, e))

    def add_all_type(self, region_url, region_name, city_name, province_name):
        for i in self.type_list:
            if i.html_type == '房产':
                house_url = region_url + '&category=' + i.code
                html_type = i.html_type
                auction_type = i.auction_type
                self.get_list_info(house_url, region_name, city_name, province_name, html_type, auction_type)

    def get_list_info(self, house_url, region_name, city_name, province_name, html_type, auction_type):
        # 判断条数 ，大于4800，正反排序
        try:
            response = s.get(house_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            count = tree.xpath('//em[@class="count"]/text()')[0]
            if int(count) == 0:
                log.info('此页面为空,url={}'.format(house_url))
                return
            elif int(count) > 4800:
                house_url_down = house_url + '&st_param=1'
                house_url_up = house_url + '&st_param=0'
                self.get_page_info(house_url_down, region_name, city_name, province_name, html_type, auction_type)
                self.get_page_info(house_url_up, region_name, city_name, province_name, html_type, auction_type)
            else:
                self.get_page_info(house_url, region_name, city_name, province_name, html_type, auction_type)
        except Exception as e:
            log.error('排序页请求错误，url="{}",e="{}"'.format(house_url, e))

    def get_page_info(self, house_url, region_name, city_name, province_name, html_type, auction_type):
        # 获取所有页数
        try:
            response = s.get(house_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            page = tree.xpath('//em[@class="page-total"]/text()')[0]
            for i in range(1, int(page) + 1):
                house_url_ = house_url + '&page=' + str(i)
                self.get_aution_info(house_url_, region_name, city_name, province_name, html_type, auction_type)
        except Exception as e:
            log.error('page页请求错误，url="{}",e="{}"'.format(house_url, e))

    def get_aution_info(self, house_url_, region_name, city_name, province_name, html_type, auction_type):
        # 获取拍卖物的信息
        try:
            response = s.get(house_url_, headers=self.headers)
            html = response.text
            item_list = re.findall('"itemUrl":"(.*?)"', html, re.S | re.M)
            for item in item_list:
                detail_url = 'http:' + item
                id_ = re.search('sf_item/(\d+)\.htm', detail_url, re.S | re.M).group(1)
                is_exist = coll.find_one({'auction_id': str(id_), 'source': source})
                if is_exist:
                    log.info('id已存在，id="{}"'.format(str(id_)))
                    continue
                self.get_detail_info(detail_url, region_name, city_name, province_name, id_, html_type, auction_type)
        except Exception as e:
            log.error('列表页请求错误，url="{}",e="{}"'.format(house_url_, e))

    def get_detail_info(self, detail_url, region_name, city_name, province_name, id_, html_type, auction_type):
        aution = Auction(source, auction_type)
        try:
            info = []
            response = s.get(detail_url, headers=self.headers)
            html = response.text
            tree = etree.HTML(html)
            aution.region = region_name
            aution.auction_id = id_
            aution.city = city_name
            aution.html_type = html_type
            aution.source_html = html
            aution.province = province_name
            aution.auction_name = tree.xpath('//div[contains(@class,"pm-main clearfix")]/h1/text()')[0].strip()
            start_auction_price = tree.xpath('//*[@id="J_HoverShow"]/tr[1]/td[1]/span[2]/span/text()')[0] \
                .replace(',', '').replace(' ', '')
            aution.start_auction_price = float(start_auction_price)
            earnest_money = tree.xpath('//*[@id="J_HoverShow"]/tr[2]/td[1]/span[2]/span/text()')[0] \
                .replace(',', '').replace(' ', '')
            aution.earnest_money = float(earnest_money)
            try:
                assess_value = tree.xpath('//*[@id="J_HoverShow"]/tr[3]/td[1]/span[2]/span/text()')[0].replace(',', '')
                aution.assess_value = float(assess_value)
            except Exception:
                aution.assess_value = None
            aution.court = tree.xpath('//p[@class="subscribe-unit"]/span/a/text()')[0]
            aution.contacts = tree.xpath('//p[@class="subscribe-unit"]/span/em/text()')[0]
            aution.phone_number = tree.xpath('//p[@class="subscribe-unit"][2]/span[2]/text()')[1]
            info.append(tree.xpath('string(//*[@id="J_DetailTabMain"]/div[4])'))
            info.append(tree.xpath('string(//*[@id="J_DetailTabMain"]/div[5])'))
            aution.info = info
            logo = tree.xpath('//h1[@class="bid-fail"]/text()')
            if logo:
                if '撤回' in logo[0] or '以物抵债' in logo[0] or '中止' in logo[0] or '暂缓' in logo[0] \
                        or '撤拍' in logo[0] or '待确认' in logo[0]:
                    return

                elif '已结束' in logo[0]:
                    # 时间字符串
                    auction_time = tree.xpath('//span[@class="countdown J_TimeLeft"]/text()')[0]
                    aution.auction_time = datetime.datetime.strptime(auction_time, "%Y/%m/%d %H:%M:%S")
                else:
                    # 时间戳
                    auction_time = tree.xpath('//li[@id="sf-countdown"]/@data-start')[0]
                    aution.auction_time = datetime.datetime.fromtimestamp(int(auction_time) / 1000)
            else:
                # 时间戳
                auction_time = tree.xpath('//li[@id="sf-countdown"]/@data-start')[0]
                aution.auction_time = datetime.datetime.fromtimestamp(int(auction_time) / 1000)
            aution.insert_db()
        except Exception as e:
            log.error('解析错误，url="{}",e="{}"'.format(detail_url, e))


if __name__ == '__main__':
    a = Ali()
    a.start_crawler()
