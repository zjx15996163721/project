import requests
from lxml import etree
import re
import pika
import json
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
from office_building_info import OfficeBuilding
p = Proxies()
p = p.get_one(proxies_number=2)

log = LogHandler('房天下')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='fangtianxia')


class FangTianXiaConsumer:

    def __init__(self, proxies):
        self.headers = {
            'Cookie': 'Integrateactivity=notincludemc; global_cookie=5j8ubb0m4ednyooi5plr4yd8023joff8i9y; __utmc=147393320; showAdhz=1; __utma=147393320.1199726105.1542094480.1542341495.1542792924.4; __utmz=147393320.1542792924.4.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E6%88%BF%E5%A4%A9%E4%B8%8B; SoufunSessionID_Office=3_1542792936_3838; searchLabelN=3_1542793018_497%5B%3A%7C%40%7C%3A%5D87edc19feb1e313acb8638b127cf7805; searchConN=3_1542793018_1305%5B%3A%7C%40%7C%3A%5D91b9570c97f179b6d0a5865bfdd42d21; newhouse_user_guid=230569EE-C2C7-F49E-C18B-B0D9CAB41DEC; newhouse_chat_guid=ADC9BD35-2591-E113-7387-3BDB937D9173; sf_source=; s=; showAdbj=1; showAdsh=1; new_search_uid=30addff46ca262cdb78c2a04acfe9736; showAdquanguo=1; polling_imei=d23d698735b7cd84; showAdzhuzhou=1; showAdmacau=1; showAdanyang=1; vh_newhouse=3_1542799696_1496%5B%3A%7C%40%7C%3A%5Dc7211a5c086643560ed38e963352a1de; indexAdvLunbo=lb_ad1%2C0%7Clb_ad2%2C0%7Clb_ad3%2C0%7Clb_ad4%2C0%7Clb_ad5%2C0%7Clb_ad6%2C0; __utmt_t0=1; __utmt_t1=1; __utmt_t2=1; city=bj; __utmt_t3=1; __utmt_t4=1; Captcha=3476637A6571767838613276454776334E626E46784F7950444B714F34576348743235626F38685A37534F4E466A4543494D795377493878374E4B69696B7A4B4974514A625861346149303D; unique_cookie=U_5j8ubb0m4ednyooi5plr4yd8023joff8i9y*114; __utmb=147393320.416.10.1542792924',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.proxies = proxies

    def parse(self, info):
        city = info['city']
        link = info['link']
        print(link)
        try:
            r = requests.get(url=link, headers=self.headers, proxies=self.proxies)
            text = r.content.decode('gbk')
        except Exception as e:
            log.error('请求失败 url={} e={}'.format(link, e))
            return
        try:
            tree = etree.HTML(text)
            region = tree.xpath('//*[@id="xfzxxq_B01_03"]/p[1]/a[3]/text()')[0]
            print(region)
        except Exception as e:
            log.error('区域错误 url={} e={}'.format(link, e))
            return
        office = OfficeBuilding('房天下')
        office.url = link
        office.city = city
        office.region = region
        try:
            name = tree.xpath('//*[@id="daohang"]/div/div[1]/dl/dd/div[1]/h1/a/text()')[0]
            print(name)
        except Exception as e:
            log.error('写字楼名称错误 url={} e={}'.format(link, e))
            return
        office.name = name

        # todo 地址 等级 写字楼类型 板块 商圈 环线
        try:
            address = re.search('楼盘地址.*?title="(.*?)">', text, re.S | re.M).group(1)
            print(address)
            if '暂无资料' in address:
                office.address = None
            else:
                office.address = address
        except:
            office.address = None
        try:
            bed_kind = re.search('写字楼级别.*?bulid-type">(.*?)</span>', text, re.S | re.M).group(1)
            print(bed_kind)
            if '暂无资料' in bed_kind:
                office.bed_kind = None
            else:
                office.bed_kind = bed_kind
        except:
            office.bed_kind = None
        try:
            office_type = re.search('物业类别.*?title="写字楼">(.*?)</div>', text, re.S | re.M).group(1).replace(' ', '').replace('\t', '').replace('\n', '')
            print(office_type)
            if '暂无资料' in office_type:
                office.office_type = None
            else:
                office.office_type = office_type
        except:
            office.office_type = None
        try:
            business_quarter = re.search('所属商圈.*?list-right">(.*?)</div>', text, re.S | re.M).group(1)
            print(business_quarter)
            if '暂无资料' in business_quarter:
                office.business_quarter = None
            else:
                office.business_quarter = business_quarter
        except:
            office.business_quarter = None
        try:
            loop_line_info = re.search('环线位置.*?list-right">(.*?)</div>', text, re.S | re.M).group(1)
            print(loop_line_info)
            if '暂无资料' in loop_line_info:
                office.loop_line_info = None
            else:
                office.loop_line_info = loop_line_info
        except:
            office.loop_line_info = None
        office.insert_db()

    def callback(self, ch, method, properties, body):
        info = json.loads(body.decode())
        self.parse(info)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='fangtianxia')
        channel.start_consuming()
