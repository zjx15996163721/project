from deal_price_info import Comm
import requests
import re
from lxml import etree
import time
import datetime
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
"""
成交价格带*号
"""
source = '乐有家'
log = LogHandler('乐有家')


class Leyoujia(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.start_url = 'https://beijing.leyoujia.com/'

    def start_crawler(self):
        try:
            res = requests.get(self.start_url, headers=self.headers, proxies=next(p))
        except Exception as e:
            log.error('请求失败, source={}, url={}, e={}'.format('乐有家', self.start_url, e))
            return
        html = etree.HTML(res.text)
        city_url_list = html.xpath("//div[@class='foot-tab-boxs clearfix']/div[1]//a/@href")
        self.city_detail(city_url_list)

    def city_detail(self, city_url_list):
        for city_url in city_url_list:
            comm_url = city_url.replace('esf', 'xq')
            try:
                city_res = requests.get(url=comm_url, headers=self.headers, proxies=next(p))
            except Exception as e:
                log.error('请求失败, source={},url={}, e={}'.format('乐有家', comm_url, e))
                continue
            html = etree.HTML(city_res.text)
            page = html.xpath("//div[@class='clearfix']//a[5]/@title")[0]
            for i in range(1, int(page)+1):
                url = comm_url + "?n=" + str(i)
                try:
                    res = requests.get(url=url, headers=self.headers, proxies=next(p))
                except Exception as e:
                    log.error('请求失败, source={}, url={}, e={}'.format('乐有家', url, e))
                    continue
                page_html = etree.HTML(res.text)
                comm_url_list = page_html.xpath("//ul[@class='xqpd_errow']/li/a/@href")
                self.comm_info(comm_url_list, city_url)

    def comm_info(self, comm_url_list, city_url):
        for comm_url in comm_url_list:
            url = city_url.replace('/esf/', comm_url)
            re_url = url.replace('xq', 'fangjia')
            try:
                res = requests.get(url=re_url, headers=self.headers, proxies=next(p))
            except Exception as e:
                log.error('请求失败, source={}, url={}, e={}'.format('乐有家', re_url, e))
                continue
            con = res.text
            co_name = re.search('wrap-head-name">(.*?)</div', con, re.S | re.M).group(1)
            co_name = co_name.strip()
            try:
                page = re.search('(\d+)">尾页', con).group(1)
            except:
                page = 1
            for i in range(1, int(page)+1):
                page_url = re_url.rstrip('.html') + "/?n=" + str(i)
                print(page_url)
                try:
                    co_res = requests.get(url=page_url, headers=self.headers, proxies=next(p))
                except Exception as e:
                    log.error('请求失败, source={}, url={}, e={}'.format('乐有家', page_url, e))
                    continue
                co_html = etree.HTML(co_res.text)
                city = co_html.xpath("//span[@class='change-city']/text()")[0].replace('\t', '').replace('[', '')
                romm_info_list = co_html.xpath("//div[@class='list-cont']/div")
                for room_info in romm_info_list:
                    room = Comm(source)
                    # 城市
                    room.city = city
                    # 小区名称
                    room.district_name = co_name
                    try:
                        # 所在楼层
                        floor = room_info.xpath(".//div[@class='text']/p[2]/span[1]/text()")[0]
                        floor = re.search('(.*?)/', floor).group(1)
                        room.floor = int(re.search('\d+', floor).group(0))
                    except:
                        room.floor = None
                    try:
                        # 总楼层
                        height = room_info.xpath(".//div[@class='text']/p[2]/span[1]/text()")[0]
                        room.height = int(re.search('/(\d+)层', height).group(1))
                    except:
                        room.height = None
                    try:
                        # 交易时间
                        trade_date = room_info.xpath(".//span[@class='cj-data-num']/text()")[0]
                        t = time.strptime(trade_date, "%Y-%m-%d")
                        y = t.tm_year
                        m = t.tm_mon
                        d = t.tm_mday
                        room.trade_date = datetime.datetime(y, m, d)
                    except:
                        room.trade_date = None
                    try:
                        # 总价
                        total_price = room_info.xpath(".//span[@class='cj-data-num c4a4a4a']/em/text()")[0]
                        if '*' in total_price:
                            log.error('source={}, 总价有问题 带*号'.format('乐有家'))
                            continue
                        else:
                            room.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
                    except:
                        room.total_price = None
                    try:
                        # 均价
                        avg_price = room_info.xpath(".//span[@class='cj-data-num']/em/text()")[0]
                        if '*' in avg_price:
                            log.error('source={}, 均价有问题 带*号'.format('乐有家'))
                            continue
                        else:
                            room.avg_price = int(re.search('(\d+)', avg_price, re.S | re.M).group(1))
                    except:
                        room.avg_price = None
                    try:
                        # 朝向
                        room.direction = room_info.xpath(".//div[@class='text']/p[2]/span[2]/text()")[0].replace('朝', '')
                    except:
                        room.direction = None
                    try:
                        region_area_info = room_info.xpath("./div[@class='text']/p[1]/text()")[1]
                    except:
                        return
                    try:
                        # 区域
                        room.region = region_area_info.split(' ')[1]
                    except:
                        room.region = None
                    try:
                        # 面积
                        size = re.search('建筑面积(.*?)平', region_area_info).group(1)
                        if size:
                            area = float(size)
                            room.area = round(area, 2)
                    except:
                        room.area = None
                    room.insert_db()

