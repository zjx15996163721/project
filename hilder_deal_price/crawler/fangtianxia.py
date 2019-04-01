import requests
import re
# from deal_price_info import Comm
from BaseClass import Base
import time
import datetime
from lxml import etree
from lib.log import LogHandler
import pika
import json
import yaml
import threading
log = LogHandler('房天下')
url = 'http://esf.sh.fang.com/newsecond/esfcities.aspx'

setting = yaml.load(open('config_local.yaml'))


class Fangtianxia(object):

    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }
        self.proxies = proxies
        self.city_list = []

    def start_crawler(self):
        response = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        html = response.text
        city_url_list = re.findall('class="red" href="(.*?)".*?>(.*?)<', html, re.S | re.M)
        for i in city_url_list[:]:
            index_url = i[0] + '/chengjiao/'
            # self.city_info(index_url, i[1])
            if len(self.city_list) == 50:
                for data in self.city_list:
                    threading.Thread(target=self.city_info, args=(data, )).start()
                self.city_list.clear()
            else:
                self.city_list.append((index_url, i[1]))
        if len(self.city_list) > 0:
            for data in self.city_list:
                threading.Thread(target=self.city_info, args=(data,)).start()

    def city_info(self, data):
        index_url = data[0]
        city = data[1]
        for i in range(1, 101):
            index_url_ = 'http:' + index_url + 'i3' + str(i) + '/'
            if i == 1:
                index_url_ = 'http:' + index_url
            try:
                response = requests.get(url=index_url_, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败, source={}, url={}, e={}'.format('房天下', index_url_, e))
                continue
            tree = etree.HTML(response.text)
            html = response.text
            try:
                # 总量
                house_num = re.search('class="org">(.*?)</b>', html, re.S | re.M).group(1)
                if house_num == '0':
                    log.info('source={}, 成交总量为0, url={}'.format('房天下', index_url_))
                    break
                city_real = re.search('city = "(.*?)"', html, re.S | re.M).group(1)
                if city != city_real:
                    break
            except Exception as e:
                log.error('没有房源, source={}, url={}, e={}'.format('房天下', index_url_, e))
                continue

            info_list = tree.xpath("//div[@class='houseList']/dl")
            for info in info_list:
                total_price = info.xpath("./dd/div[3]/p[1]/span[1]/text()")[0]
                if '*' in total_price:
                    log.info('总价有问题 带*号')
                    continue
                # 没有问题的进详情页抓取
                # 链接
                half_house_link = info.xpath("./dd/p[1]/a/@href")[0]
                house_link = re.search('(.*?)/chengjiao', index_url_, re.S | re.M).group(1) + half_house_link
                # id
                house_id_info = info.xpath("./dd/p[4]/a[2]/@href")[0]
                house_id = re.search('/house-xm(\d+)/', house_id_info, re.S | re.M).group(1)
                self.get_page_num(house_link, house_id, city)

    def get_page_num(self, url, house_id, city):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'],
                                                                       port=setting['rabbit']['port'],
                                                                       heartbeat=0))
        channel = connection.channel()

        detail_url = re.search('(.*?)/chengjiao', url, re.S | re.M).group(1) + '/NewSecond/Include/DealHouseList.aspx?projcode={}&pageindex={}'.format(house_id, '1')
        try:
            response = requests.get(url=detail_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 url={}, source={}, e={}'.format(detail_url, '房天下', e))
            return
        try:
            tree = etree.HTML(response.text)
            max_num_info = tree.xpath("//div[@id='chengjiaoxq_B08_01']/span/text()")[0]
            max_num = re.search("共(\d+)页", max_num_info, re.S | re.M).group(1)
        except Exception as e:
            log.error('获取页码失败source={} text={}'.format('房天下', response.text))
            return
        for num in range(1, int(max_num) + 1):
            detail_url_new = re.search('(.*?)/chengjiao', url, re.S | re.M).group(1) + '/NewSecond/Include/DealHouseList.aspx?projcode={}&pageindex={}'.format(house_id, str(num))
            data = {
                'detail_url_new': detail_url_new,
                'city': city,
            }
            channel.queue_declare(queue='fangtianxia')
            channel.basic_publish(exchange='',
                                  routing_key='fangtianxia',
                                  body=json.dumps(data))
            log.info('source={}, 放队列 {}'.format('房天下', data))

    # 下面的解析不用看了,在消费者里面有
    def parse(self, url, city):
        try:
            response = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败,source="{}", url="{}",e="{}"'.format('房天下', url, e))
            return
        tree = etree.HTML(response.text)
        info_list = tree.xpath("//div[@class='houseList']/dl")
        comm = Base('房天下')
        comm.url = url
        comm.city = city
        for info in info_list:
            district_name_info = info.xpath("./dd/p/a/text()")[0]
            # 小区名称
            comm.district_name = district_name_info.split(' ')[0]
            if '�' in comm.district_name:
                log.error('source={}, 网页出现繁体字, url={}'.format('房天下', url))
                break
            # 室
            try:
                comm.room = int(re.search('(\d+)室', district_name_info, re.S | re.M).group(1))
            except Exception as e:
                comm.room = None
            # 厅
            try:
                comm.hall = int(re.search('(\d+)厅', district_name_info, re.S | re.M).group(1))
            except Exception as e:
                comm.hall = None
            # 面积
            try:
                comm.area = float(re.search('(\d+\.?\d+?)平米', district_name_info, re.S | re.M).group(1))
            except Exception as e:
                comm.area = None
            # 区域
            try:
                region_info = info.xpath("./dd/p[2]/text()")[0]
                comm.region = region_info.split('-')[0]
            except Exception as e:
                comm.region = None
            # 朝向 总楼层
            try:
                direction_info = info.xpath("./dd/p[3]")[0]
                direction_info = direction_info.xpath('string(.)')
                comm.direction = direction_info.split('|')[0]
                comm.height = int(re.search('\(共(.*?)层\)', direction_info, re.S | re.M).group(1))
            except Exception as e:
                comm.direction = None
                comm.height = None
            # 时间
            try:
                trade_date = info.xpath("./dd/div[2]/p[1]/text()")[0]
                t = time.strptime(trade_date, "%Y-%m-%d")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                comm.trade_date = datetime.datetime(y, m, d)
            except Exception as e:
                comm.trade_date = None
            # 总价
            try:
                total_price = info.xpath("./dd/div[3]/p[1]/span[1]/text()")[0]
                comm.total_price = int(total_price) * 10000
            except Exception as e:
                comm.total_price = None
            # 均价
            try:
                avg_price_info = info.xpath("./dd/div[3]/p[2]/b[1]/text()")[0]
                comm.avg_price = int(re.search("(\d+)元", avg_price_info, re.S | re.M).group(1))
            except Exception as e:
                comm.avg_price = None
            comm.insert_db()

