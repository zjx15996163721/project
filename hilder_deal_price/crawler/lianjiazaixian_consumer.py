import requests
import re
from BaseClass import Base
from Base_to235 import Child
import time
import datetime
from lib.log import LogHandler
from lxml import etree
import pika
import json
import yaml
log = LogHandler('链家在线')

setting = yaml.load(open('config_local.yaml'))


class LianJiaConsumer:

    def __init__(self, proxies):
        self.headers = {
            'Cookie': 'TY_SESSION_ID=93f4e4f8-68f2-431f-9eb4-eee9f3a67f40; all-lj=8e5e63e6fe0f3d027511a4242126e9cc; lianjia_uuid=602795b2-d2ac-441b-8c39-e9d1f2f69c0b; _smt_uid=5bea30ce.66e4f57; _jzqc=1; _qzjc=1; UM_distinctid=1670aceae1de93-0bd892eb8bcfc4-162a1c0b-1fa400-1670aceae1e38a; _ga=GA1.2.605174491.1542074580; TY_SESSION_ID=13c51829-a6c7-4a58-99b3-90ef353caff6; ljref=pc_sem_baidu_ppzq_x; select_city=310000; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1542074574,1542787625,1542890281,1543076274; CNZZDATA1253492439=1141211633-1542074097-%7C1543073363; CNZZDATA1254525948=1126027712-1542070053-%7C1543072024; CNZZDATA1255633284=2013564234-1542069500-%7C1543071746; CNZZDATA1255604082=774565866-1542071106-%7C1543075953; _jzqa=1.360625764904573300.1542074575.1542977789.1543076275.17; _jzqy=1.1542787625.1543076275.2.jzqsr=baidu|jzqct=l%E9%93%BE%E5%AE%B6%E5%9C%B0%E4%BA%A7.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6; _jzqckmp=1; lianjia_ssid=28c1a500-4fb3-4788-8319-3078662ab36c; _gid=GA1.2.400725004.1543076276; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1543076434; _qzja=1.2087566050.1542074574679.1542890281900.1543076274583.1543076426913.1543076434630.0.0.0.62.6; _qzjb=1.1543076274583.8.0.0.0; _qzjto=8.1.0; _jzqb=1.8.10.1543076275.1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'],
                                                                            port=setting['rabbit']['port'],
                                                                            heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='lianjia')
        self.proxies = proxies
        self.lianjia_list = []

    def final_parse(self, data):
        final_url = data['link']
        city = data['city']
        region = data['region']
        try:
            r = requests.get(url=final_url, headers=self.headers, proxies=self.proxies, timeout=60)
        except Exception as e:
            log.error('请求失败, source={}, 没有更多小区成交 url={}, e={}'.format('链家在线', final_url, e))
            return
        tree = etree.HTML(r.text)
        url_list = tree.xpath("//ul[@class='listContent']/li")
        if url_list:
            for info in url_list:
                comm = Base('链家在线')
                comm.url = final_url
                # 区域
                comm.region = region.strip()
                # 城市
                comm.city = city.strip()
                district_name_room_area = info.xpath("./div/div[@class='title']/a/text()")[0]
                # 小区名称
                comm.district_name = district_name_room_area.split(' ')[0]
                try:
                    room_hall = district_name_room_area.split(' ')[1]
                except:
                    room_hall = None
                try:
                    # 室
                    comm.room = int(re.search('(\d+)室', room_hall, re.S | re.M).group(1))
                except:
                    comm.room = None
                try:
                    # 厅
                    comm.hall = int(re.search('(\d+)厅', room_hall, re.S | re.M).group(1))
                except:
                    comm.hall = None
                try:
                    # 面积
                    area = district_name_room_area.split(' ')[2]
                    area = re.search("(.*?)平米", area, re.S | re.M).group(1)
                    comm.area = round(float(area), 2)
                except:
                    comm.area = None
                try:
                    direction_fitment = info.xpath("./div/div[@class='address']/div[1]/text()")[0].split('|')
                    # 朝向
                    comm.direction = direction_fitment[0]
                    # 装修
                    comm.fitment = direction_fitment[1]
                except:
                    comm.direction = None
                    comm.fitment = None
                # 总楼层
                try:
                    height = info.xpath("./div/div[@class='flood']/div[1]/text()")[0]
                    comm.height = int(re.search("共(\d+)层", height, re.S | re.M).group(1))
                except:
                    comm.height = None
                # # 总价
                # try:
                #     total_price = info.xpath("./div/div[@class='address']/div[3]/span/text()")[0]
                #     if "*" in total_price:
                #         log.error('source={}, 总价有问题 带*号'.format('链家在线'))
                #         continue
                #     else:
                #         comm.total_price = int(total_price) * 10000
                # except:
                #     comm.total_price = None
                # 交易时间
                try:
                    trade_date = info.xpath("./div/div[@class='address']/div[2]/text()")[0]
                    t = time.strptime(trade_date, "%Y.%m.%d")
                    y = t.tm_year
                    m = t.tm_mon
                    d = t.tm_mday
                    comm.trade_date = comm.local2utc(datetime.datetime(y, m, d))
                except:
                    comm.trade_date = None
                # 均价
                try:
                    avg_price = info.xpath("./div/div[@class='flood']/div[3]/span/text()")[0]
                    comm.avg_price = int(avg_price)
                except:
                    comm.avg_price = None
                try:
                    comm.total_price = int(int(comm.avg_price)*float(comm.area))
                except:
                    comm.total_price = None
                comm.insert_db()

    def get_detail_info(self, data):
        url = data['link']
        city = data['city']
        region = data['region']
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies, timeout=60)
        except Exception as e:
            print(e)
            self.channel.basic_publish(exchange='',
                                       routing_key='lianjia',
                                       body=json.dumps(data))
            log.info('放队列 {}'.format(data))
            return
        tree = etree.HTML(r.text)
        c = Child()
        c.url = url
        c.source = '链家在线'
        c.city = city
        c.region = region

        # 面积
        try:
            area = re.search('建筑面积</span>(.*?)</li>', r.text, re.S | re.M).group(1)
            area = float(area.replace('㎡', ''))
        except:
            area = None
        c.area = area

        # 户型
        try:
            main_type = re.search('房屋户型</span>(.*?)</li>', r.text, re.S | re.M).group(1).replace(' ', '')
        except:
            main_type = None
        c.main_type = main_type

        # 装修情况
        try:
            fitment = re.search('装修情况</span>(.*?)</li>', r.text, re.S | re.M).group(1)
        except:
            fitment = None
        c.fitment = fitment

        # 朝向
        try:
            direction = re.search('房屋朝向</span>(.*?)</li>', r.text, re.S | re.M).group(1)
        except:
            direction = None
        c.direction = direction

        # 建成年代
        try:
            create_year = re.search('建成年代</span>(.*?)</li>', r.text, re.S | re.M).group(1)
        except:
            create_year = None
        c.create_year = create_year

        # 挂牌价
        try:
            listing_price = re.search('<label>(.*?)</label>挂牌价格', r.text, re.S | re.M).group(1)
            listing_price = int(listing_price) * 10000
        except:
            listing_price = None
        c.listing_price = listing_price

        # 成交周期
        try:
            deal_cycle = re.search('挂牌价格.*?<label>(.*?)</label>成交周期', r.text, re.S | re.M).group(1)
        except:
            deal_cycle = None
        c.deal_cycle = deal_cycle

        # 成交时间
        try:
            trade_date = tree.xpath('//div[@class="wrapper"]/span/text()')[0].replace(' ', '').replace('成交', '')
            t = time.strptime(trade_date, "%Y.%m.%d")
            y = t.tm_year
            m = t.tm_mon
            d = t.tm_mday
            trade_date = Base.local2utc(datetime.datetime(y, m, d))
        except:
            trade_date = None
        c.trade_date = trade_date

        # 挂牌时间
        try:
            listing_date = re.search('挂牌时间</span>(.*?)</li>', r.text, re.S | re.M).group(1).replace(' ', '')
            t = time.strptime(listing_date, "%Y-%m-%d")
            y = t.tm_year
            m = t.tm_mon
            d = t.tm_mday
            listing_date = Base.local2utc(datetime.datetime(y, m, d))
        except:
            listing_date = None
        c.listing_date = listing_date

        # 小区
        try:
            district_name = tree.xpath('//div[@class="wrapper"]/h1/text()')[0].split(' ')[0]
        except:
            district_name = None
        c.district_name = district_name

        # 调价次数
        try:
            adjust_price_count = re.search('成交周期.*?<label>(.*?)</label>调价', r.text, re.S | re.M).group(1)
            adjust_price_count = int(adjust_price_count)
        except:
            adjust_price_count = None
        c.adjust_price_count = adjust_price_count

        # 单价    avg_price  元
        try:
            avg_price = tree.xpath('//div[@class="price"]/b/text()')[0]
            avg_price = int(avg_price)
        except:
            avg_price = None
        c.avg_price = avg_price

        # 总价     total_price
        # total_price = tree.xpath('//div[@class="price"]/span/i/text()')[0]
        try:
            total_price = int(avg_price * area)
        except:
            total_price = None
        c.total_price = total_price

        # 配备电梯
        try:
            packing_space = re.search('配备电梯</span>(.*?)</li>', r.text, re.S | re.M).group(1)
            if '有' in packing_space:
                packing_space = True
            elif '无' in packing_space:
                packing_space = False
        except:
            packing_space = False
        c.packing_space = packing_space

        c.insert_db()

        # todo 匹配 物业类型  地址

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        self.final_parse(data)

        # self.get_detail_info(data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='lianjia')
        self.channel.start_consuming()
