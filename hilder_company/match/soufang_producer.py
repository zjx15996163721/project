"""
搜房网站抓取
http://www.sofang.com/
"""
import requests
from lxml import etree
import re
import pika
import json
from lib.log import LogHandler
log = LogHandler('搜房')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
channel = connection.channel()


class SouFangRent(object):

    def __init__(self, proxies, cookie):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie': cookie
        }
        self.start_url = 'http://www.sofang.com/city.html'
        self.proxies = proxies

    def get_all_city_url(self):
        r = requests.get(url=self.start_url, headers=self.headers, proxies=self.proxies)
        tree = etree.HTML(r.text)
        links = tree.xpath("//div[@class='citys']/ul/li/p/a")
        city_dict = {}
        for link in links:
            url = link.xpath("./@href")[0]
            city = link.xpath("./text()")[0]
            city_dict[city] = url
        self.get_office_buliding(city_dict)

    def get_office_buliding(self, city_dict):
        for city in city_dict:
            city_url = city_dict[city] + '/xzlrent/build'   # 写字楼出租 楼盘查询
            print(city_url)
            try:
                r = requests.get(url=city_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败 url={} e={}'.format(city_url, e))
                continue
            try:
                tree = etree.HTML(r.text)
                max_page = tree.xpath("//div[@class='page_nav']/ul/li/a/@alt")[-1]
                for num in range(1, int(max_page) + 1):
                    page_url = city_url + '/bl{}?'.format(num)
                    self.get_all_links(page_url, city)
            except Exception as e:
                log.info('没有写字楼数据')
                page_url = city_url + '/bl{}?'.format(1)
                self.get_all_links(page_url, city)

    def get_all_links(self, page_url, city):
        try:
            response = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 e={}'.format(e))
            return
        tree = etree.HTML(response.text)
        buildings = tree.xpath("//div[@class='list list_free']/dl")
        for building in buildings:
            half_url = building.xpath("./dd[1]/p/a/@href")[0]
            # 写字楼链接
            url = re.search('(.*?)/xzlrent', page_url, re.S | re.M).group(1) + half_url
            # 写字楼名称
            office_name = building.xpath("./dd[1]/p/a/text()")[0]
            try:
                # 出租价格
                rent_price = float(building.xpath("./dd[2]/p[1]/span/text()")[0])
            except:
                rent_price = None
            data = {
                'url': url,
                'city': city,
                'office_name': office_name,
                'rent_price': rent_price
            }
            channel.queue_declare(queue='soufang_rent')
            channel.basic_publish(exchange='',
                                  routing_key='soufang_rent',
                                  body=json.dumps(data))
            log.info('一条数据放队列 url={}'.format(data))


class SouFangSale(SouFangRent):

    def __init__(self, proxies, cookie):
        super(SouFangSale, self).__init__(proxies, cookie)

    def get_office_buliding(self, city_dict):
        for city in city_dict:
            city_url = city_dict[city] + '/xzlsale/area'   # 写字楼出售
            print(city_url)
            try:
                r = requests.get(url=city_url, headers=self.headers, proxies=self.proxies)
                try:
                    tree = etree.HTML(r.text)
                    max_page = tree.xpath("//div[@class='page_nav']/ul/li/a/@alt")[-1]
                    for num in range(1, int(max_page)+1):
                        page_url = city_url + '/bl{}?'.format(num)
                        self.get_all_links(page_url, city)
                except Exception as e:
                    log.info('没有写字楼数据')
            except Exception as e:
                log.error('请求失败 e={}'.format(e))

    def get_all_links(self, page_url, city):
        try:
            response = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
            tree = etree.HTML(response.text)
            buildings = tree.xpath("//div[@class='list list_free']/dl")
            for building in buildings:
                half_url = building.xpath("./dd[1]/p/a/@href")[0]
                # 写字楼链接
                url = re.search('(.*?)/xzlsale', page_url, re.S | re.M).group(1) + half_url
                try:
                    # 出售价格
                    sell_price = float(building.xpath("./dd[2]/p[1]/span/text()")[0])*10000.0
                except:
                    sell_price = None
                try:
                    # 均价
                    avg_price = int(building.xpath("./dd[2]/p[2]/span/text()")[0])
                except:
                    avg_price = None
                try:
                    # 物业类型
                    estate_type2 = building.xpath("./dd[1]/div/p[2]/span[1]/text()")[0]
                except:
                    estate_type2 = None
                try:
                    # 建筑面积
                    build_area_info = building.xpath("./dd[1]/div/p[2]/span[3]/text()")[0]
                    build_area = re.search('(\d+)', build_area_info, re.S | re.M).group(1)
                except:
                    build_area = None
                try:
                    # 楼层
                    floor_info = building.xpath("./dd[1]/div/p[2]/span[5]/text()")[0]
                    total_floor = re.search('/(\d+)', floor_info, re.S | re.M).group(1)
                    floor = re.search('(\d+)/', floor_info, re.S | re.M).group(1)
                except:
                    total_floor = None
                    floor = None
                data = {
                    'url': url,
                    'city': city,
                    'sell_price': sell_price,
                    'avg_price': avg_price,
                    'estate_type2': estate_type2,
                    'build_area': build_area,
                    'total_floor': total_floor,
                    'floor': floor
                }
                channel.queue_declare(queue='soufang_sale')
                channel.basic_publish(exchange='',
                                      routing_key='soufang_sale',
                                      body=json.dumps(data))
                log.info('一条数据放队列 url={}'.format(data))
        except Exception as e:
            log.error('请求失败 e={}'.format(e))