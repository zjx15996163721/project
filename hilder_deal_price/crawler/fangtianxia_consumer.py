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
log = LogHandler('房天下')

setting = yaml.load(open('config_local.yaml'))


class FangtianxiaConsumer(object):

    def __init__(self, proxies):
        self.headers = {
            'Cookie': 'Integrateactivity=notincludemc; global_cookie=5j8ubb0m4ednyooi5plr4yd8023joff8i9y; __utmc=147393320; __utmz=147393320.1542792924.4.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E6%88%BF%E5%A4%A9%E4%B8%8B; SoufunSessionID_Office=3_1542792936_3838; searchLabelN=3_1542793018_497%5B%3A%7C%40%7C%3A%5D87edc19feb1e313acb8638b127cf7805; searchConN=3_1542793018_1305%5B%3A%7C%40%7C%3A%5D91b9570c97f179b6d0a5865bfdd42d21; newhouse_user_guid=230569EE-C2C7-F49E-C18B-B0D9CAB41DEC; newhouse_chat_guid=ADC9BD35-2591-E113-7387-3BDB937D9173; sf_source=; s=; new_search_uid=30addff46ca262cdb78c2a04acfe9736; vh_newhouse=3_1542799696_1496%5B%3A%7C%40%7C%3A%5Dc7211a5c086643560ed38e963352a1de; __utma=147393320.1199726105.1542094480.1542792924.1542808263.5; Captcha=3967693962662B5A583635494859525659394A757348674F76576F576D754F56384D3353666E334A4952536632642F7769322B7030306D30456F6B4D6D3346454B5444646E75302B6648553D; city=bj; unique_cookie=U_5j8ubb0m4ednyooi5plr4yd8023joff8i9y*150',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.proxies = proxies
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'],
                                                                            port=setting['rabbit']['port'],
                                                                            heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='fangtianxia')
        self.fang_list = []

    def parse(self, data):
        url = data['detail_url_new']
        city = data['city']
        try:
            response = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败，source="{}"，url="{}",e="{}"'.format('房天下', url, e))
            return
        tree = etree.HTML(response.text)
        try:
            info_list = tree.xpath("//div[@class='houseList']/dl")
        except Exception as e:
            log.error('解析错误，source="{}"，url="{}",e="{}"'.format('房天下', url, e))
            return
        comm = Base('房天下')
        comm.url = url
        comm.city = city
        for info in info_list:
            try:
                district_name_info = info.xpath("./dd/p/a/text()")[0]
            except:
                continue
            # 小区名称
            comm.district_name = district_name_info.split(' ')[0]
            if '�' in comm.district_name:
                log.error('source={}, 网页出现繁体字, url={}'.format('房天下', url))
                break
            # 室
            try:
                comm.room = int(re.search('(\d+)室', district_name_info, re.S | re.M).group(1))
            except:
                comm.room = None
            # 厅
            try:
                comm.hall = int(re.search('(\d+)厅', district_name_info, re.S | re.M).group(1))
            except:
                comm.hall = None
            # 面积
            try:
                comm.area = float(re.search('(\d+\.?\d+?)平米', district_name_info, re.S | re.M).group(1))
            except:
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
                comm.trade_date = comm.local2utc(datetime.datetime(y, m, d))
            except Exception as e:
                comm.trade_date = None
            # 总价
            # try:
            #     total_price = info.xpath("./dd/div[3]/p[1]/span[1]/text()")[0]
            #     comm.total_price = int(total_price) * 10000
            # except Exception as e:
            #     comm.total_price = None
            # 均价
            try:
                avg_price_info = info.xpath("./dd/div[3]/p[2]/b[1]/text()")[0]
                comm.avg_price = int(re.search("(\d+)元", avg_price_info, re.S | re.M).group(1))
            except Exception as e:
                comm.avg_price = None
            # 总价
            try:
                comm.total_price = int(int(comm.avg_price)*float(comm.area))
            except:
                comm.total_price = None
            comm.insert_db()

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        self.parse(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='fangtianxia')
        self.channel.start_consuming()
