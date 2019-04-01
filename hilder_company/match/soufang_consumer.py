import requests
from lxml import etree
import re
import pika
import json
from bs4 import BeautifulSoup
from retry import retry
import time
import sys
sys.setrecursionlimit(1000000)
from lib.proxy_iterator import Proxies
from lib.log import LogHandler
from office_building_info import OfficeBuilding
log = LogHandler('搜房')
p = Proxies()
p = p.get_one(proxies_number=3)


class Rent(object):

    def __init__(self, proxies, cookie):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Cookie': cookie
        }
        self.proxies = proxies
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()

    # @retry(delay=1, tries=3)
    def get_data_rent(self, url, city, office_name, rent_price):
        try:
            # S = requests.session()
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            print(url)
            while '验证失败' not in r.text:
                self.parse_rent(r, city, office_name, rent_price)
                return
            while '验证失败' in r.text:
                cookies = re.search("token = '(.*?)'", r.text, re.S | re.M).group(1)
                self.channel.close()
                return self.restart(cookies)
        except Exception as e:
            log.error('请求失败 url={}'.format(url))

    def restart(self, cookies):
        rent = Rent(p, cookies)
        rent.start_consuming_rent()

    def parse_rent(self, r, city, office_name, rent_price):
        tree = etree.HTML(r.text)
        office = OfficeBuilding('搜房')
        office.city = city
        office.name = office_name
        # 租售类型
        office.rent_type = '出租'
        try:
            # 建筑类型
            build_type = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[1]/span/text()")[0]
            office.build_type = build_type
        except:
            office.build_type = None
        # try:
        #     # 建筑结构
        #     build_structure = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[2]/span/text()")[0]
        #     office.build_structure = build_structure
        # except:
        #     office.build_structure = None
        try:
            # 项目特色
            characteristic = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[3]/span/text()")[0]
            office.characteristic = characteristic
        except:
            office.characteristic = None
        # 建筑面积 出租价格
        try:
            build_area_info = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[4]/span/text()")[0]
            build_area = re.search('(\d+)', build_area_info, re.S | re.M).group(1)
            office.build_area = build_area
            # if rent_price:
            #     office.rent_price = float(rent_price) * float(build_area) * 30.0
        except:
            build_area = None
            office.build_area = build_area
            # office.rent_price = rent_price
        # 占地面积
        try:
            all_area_info = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[5]/span/text()")[0]
            all_area = re.search('(\d+)', all_area_info, re.S | re.M).group(1)
            office.all_area = all_area
        except:
            all_area = None
            office.all_area = all_area
        # # 总户数
        # try:
        #     household_count_info = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[6]/span/text()")[0]
        #     household_count = re.search('(\d+)', household_count_info, re.S | re.M).group(1)
        #     office.household_count = household_count
        # except:
        #     household_count = None
        #     office.household_count = household_count
        try:
            # 绿化率
            virescence_percent = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[7]/span/text()")[0]
            office.virescence_percent = virescence_percent
        except:
            office.virescence_percent = None
        try:
            # 容积率
            cubage_percent = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[8]/span/text()")[0]
            office.cubage_percent = cubage_percent
        except:
            office.cubage_percent = None
        try:
            # 区域
            region = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[9]/span/text()")[0].replace('\r', '').replace('\n', '').replace('\t', '')
            office.region = region
            print(office.region)
        except:
            office.region = None
            print(office.region)
        # # 电话
        # try:
        #     mobile_info = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[10]/span/text()")[0]
        #     mobile = re.search('(\d+)', mobile_info, re.S | re.M).group(1)
        #     office.mobile = mobile
        # except:
        #     mobile = None
        #     office.mobile = mobile
        # 物业费
        try:
            estate_charge_info = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[12]/span/text()")[0]
            estate_charge = re.search('(\d+\.?\d+)|(\d+)', estate_charge_info, re.S | re.M).group()
            office.estate_charge = estate_charge
            print(office.estate_charge)
        except:
            office.estate_charge = None
            print(office.estate_charge)
        try:
            # 开发商
            developer = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[13]/span/text()")[0]
            office.developer = developer
        except:
            office.developer = None
        try:
            # 物业公司
            estate_company = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[14]/span/text()")[0]
            office.estate_company = estate_company
        except:
            office.estate_company = None
        try:
            # 地址
            address = tree.xpath("//div[@class='real_detail detail_tit']/ul/li[15]/span/text()")[0]
            office.address = address
        except:
            office.address = None
        # # 外景图
        # try:
        #     out_pics = []
        #     out_pics_info = tree.xpath("//div[@class='detail_picbot_mid']/ul/li")
        #     for pics_info in out_pics_info:
        #         pic = pics_info.xpath("./a/img/@src")[0]
        #         out_pics.append(pic)
        #     office.out_pics = out_pics
        # except:
        #     out_pics = None
        #     office.out_pics = out_pics
        office.insert_db()

    def callback(self, ch, method, properties, body):
        info = json.loads(body.decode())
        url = info['url']
        city = info['city']
        office_name = info['office_name']
        rent_price = info['rent_price']
        self.get_data_rent(url, city, office_name, rent_price)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_rent(self):
        self.channel.queue_declare(queue='soufang_rent')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='soufang_rent')
        self.channel.start_consuming()


class Sale(Rent):

    def __init__(self, proxies, cookie):
        super(Sale, self).__init__(proxies, cookie)

    def get_data_sale(self, url, city, sell_price, avg_price, estate_type2, build_area, total_floor, floor):
        try:
            # S = requests.session()
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            print(r.text)
            while '验证失败' not in r.text:
                self.parse_sale(r, city, sell_price, avg_price, estate_type2, build_area, total_floor, floor)
                return
            while '验证失败' in r.text:
                cookies = re.search("token = '(.*?)'", r.text, re.S | re.M).group(1)
                self.channel.close()
                # clear()
                sale = Sale(next(p), cookies)
                sale.start_consuming_sale()
                return
        except Exception as e:
            log.error('请求失败 url={}'.format(url))

    def parse_sale(self, r, city, sell_price, avg_price, estate_type2, build_area, total_floor, floor):
        tree = etree.HTML(r.text)
        office = OfficeBuilding('搜房')
        # 租售类型
        office.rent_type = '出售'
        # 城市
        office.city = city
        # 出售价格
        office.sell_price = sell_price
        # 均价
        office.avg_price = avg_price
        # 物业类型
        office.estate_type2 = estate_type2
        # 建筑面积
        office.build_area = build_area
        # 总楼层
        office.total_floor = total_floor
        # 建筑楼层
        office.floor = floor
        try:
            # 区域
            region = tree.xpath("//p[@class='menu_nav']/a[3]/text()")[0]
            office.region = region
        except:
            office.region = None
        try:
            # 板块
            block = tree.xpath("//p[@class='menu_nav']/a[4]/text()")[0]
            office.block = block
        except:
            office.block = None
        try:
            # 名称
            name = tree.xpath("//p[@class='menu_nav']/a[5]/text()")[0]
            office.name = name
        except:
            office.name = None
        info = tree.xpath("//div[@class='info_r']/ul[@class='msg']/li")
        for i in info:
            i_name = i.xpath("./label/text()")[0]
            if '建筑面积' in i_name:
                pass
            elif '物业费' in i_name:
                # 物业费
                i_value = i.xpath("./span/text()")[0]
                estate_charge = re.search('(\d+)', i_value, re.S | re.M).group(1)
                office.estate_charge = str(float(estate_charge) * float(office.build_area))
                print(office.estate_charge)
            elif '所在楼层' in i_name:
                pass
            elif '物业类型' in i_name:
                pass
            elif '装修状况' in i_name:
                # 装修状况
                i_value = i.xpath("./span/text()")[0]
                office.fitment = i_value
            elif '工位数量' in i_name:
                pass
            elif '楼盘名称' in i_name:
                pass
            elif '所属区域' in i_name:
                # 地址
                i_value = i.xpath("./span[2]/text()")[0]
                office.address = i_value
        # 电话
        mobile = tree.xpath("//div[@class='broker_info']/dl/dd/p[2]/text()")[0]
        office.mobile = mobile
        # 外景图
        out_pics = []
        out_pics_info = tree.xpath("//div[@class='detail_picbot_mid']/ul/li")
        for pics_info in out_pics_info:
            pic = pics_info.xpath("./a/img/@src")[0]
            out_pics.append(pic)
        office.out_pics = out_pics
        # # 描述 html
        # soup = BeautifulSoup(r.text, 'lxml')
        # description = soup.select(".depict")[0]
        # office.description = str(description)
        # office.insert_db()

    def callback(self, ch, method, properties, body):
        info = json.loads(body.decode())
        url = info['url']
        city = info['city']
        sell_price = info['sell_price']
        avg_price = info['avg_price']
        estate_type2 = info['estate_type2']
        build_area = info['build_area']
        total_floor = info['total_floor']
        floor = info['floor']
        self.get_data_sale(url, city, sell_price, avg_price, estate_type2, build_area, total_floor, floor)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_sale(self):
        self.channel.queue_declare(queue='soufang_sale')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='soufang_sale')
        self.channel.start_consuming()
