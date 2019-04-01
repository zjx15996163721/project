# from deal_price_info import Comm
from BaseClass import Base
import requests
import re
from lxml import etree
from lib.log import LogHandler
import time
import datetime
import json

log = LogHandler('中原地产')
source = '中原地产'


class Centaline(object):

    def __init__(self, proxies):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.start_url = 'http://www.centaline.com.cn/'
        self.proxies = proxies

    def start_crawler(self):
        res = requests.get(url=self.start_url, headers=self.headers, proxies=self.proxies)
        res.encoding = 'gbk'
        second_city_list = re.findall('https?://\w+.centanet.com/ershoufang/', res.text, re.S | re.M)
        for city in second_city_list:
            city_comm = city.replace('ershoufang', 'xiaoqu')
            if 'sh' in city_comm:
                try:
                    city_res = requests.get(url=city_comm, headers=self.headers, proxies=self.proxies)
                except Exception as e:
                    log.error('请求失败 source={}, url={}, e={}'.format('中原地产', city_comm, e))
                    continue
                city_res.encoding = 'gbk'
                city_html = etree.HTML(city_res.text)
                # 上海
                page_str = city_html.xpath("//a[@class='fsm fb']/@href")[0]
                page = re.search('\d+', page_str).group(0)
                for i in range(1, int(page) + 1):
                    url = city_comm + "g" + str(i)
                    try:
                        comm_res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
                    except Exception as e:
                        log.error('source={}, 请求失败 url={}, e={}'.format('中原地产', url, e))
                        continue
                    html = etree.HTML(comm_res.text)
                    comm_url_list = html.xpath("//ul/li/div/a/@href")
                    self.comm_detail(comm_url_list, city_comm)
            else:
                try:
                    city_res = requests.get(url=city_comm, headers=self.headers, proxies=self.proxies)
                except Exception as e:
                    log.error('请求失败 source={}, url={}, e={}'.format('中原地产', city_comm, e))
                    continue
                city_res.encoding = 'gbk'
                city_html = etree.HTML(city_res.text)
                # 北京等城市
                try:
                    page_str = city_html.xpath("//a[@class='fsm fb']/@href")[1]
                    page = re.search('\d+', page_str).group(0)
                except Exception as e:
                    log.error('页面信息不存在 source={}, url={}, e={}'.format('中原地产', city_comm, e))
                    continue
                for i in range(1, int(page) + 1):
                    url = city_comm + "g" + str(i)
                    try:
                        comm_res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
                    except Exception as e:
                        log.error('请求失败 source={}, url={}, e={}'.format('中原地产', url, e))
                        continue
                    html = etree.HTML(comm_res.text)
                    comm_url_list = html.xpath("//div[@class='section']/div/div[1]/h4/a/@href")
                    self.comm_detail_new(comm_url_list, city_comm)

    def comm_detail(self, comm_url_list, city):
        for comm_url in comm_url_list[1:]:
            com_url = city.replace('/xiaoqu/', comm_url)
            statecode = re.search('xq-(.*)', comm_url).group(1)
            # R S 两种不同的接口 S代表出售 R代表出租 这里用S
            comm_detail_url = 'http://sh.centanet.com/apipost/GetDealRecord?estateCode=' + statecode + '&posttype=S&pageindex=1&pagesize=10000'
            try:
                com_res = requests.get(url=com_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('source={}, 请求失败 url={} e={}'.format('中原地产', com_url, e))
                continue
            try:
                res = requests.get(url=comm_detail_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('source={}, 请求失败 url={} e={}'.format('中原地产', comm_detail_url, e))
                continue
            html = etree.HTML(com_res.text)
            try:
                data_dict = json.loads(res.text)
            except Exception as e:
                log.error('source={}, 序列化失败 e={}'.format('中原地产', e))
                continue
            try:
                district_name = html.xpath("//div/h3/text()")[0]
                city_name = html.xpath("//div[@class='idx-city']/text()")[0].replace('\n', '').replace('\t', '').replace(' ', '')
                region = html.xpath("//a[@class='f000']/text()")[0].replace('\n', '').replace('\t', '').replace(' ', '')
            except Exception as e:
                log.error('source={}, 区域解析失败 e={}'.format('中原地产', e))
                continue
            for data in data_dict["result"]:
                co = Base(source)
                # 小区名称
                co.district_name = district_name.strip()
                # 区域
                co.region = region
                # 城市
                co.city = city_name
                try:
                    room_type = data["houseType"]
                    # 室数
                    co.room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
                except Exception as e:
                    co.room = None
                    log.error('source={}, room为空 e={}'.format('中原地产', e))
                try:
                    room_type = data["houseType"]
                    # 厅数
                    co.hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
                except Exception as e:
                    co.hall = None
                    log.error('source={}, hall e={}'.format('中原地产', e))
                # 面积
                area = data['areaSize'].replace('平', '')
                if area:
                    area = float(area)
                    co.area = round(area, 2)
                # 朝向
                co.direction = data['direction']
                # 交易时间
                trade_date = '20' + data['dealTime']
                if trade_date:
                    t = time.strptime(trade_date, "%Y-%m-%d")
                    y = t.tm_year
                    m = t.tm_mon
                    d = t.tm_mday
                    co.trade_date = co.local2utc(datetime.datetime(y, m, d))
                try:
                    # 均价
                    avg_price = data['unitPrice']
                    avg_price = int(float(re.search('(\d+\.?\d+)', avg_price, re.S | re.M).group(1)) * 10000)
                    co.avg_price = avg_price
                except:
                    co.avg_price = None
                # 总价
                # total_price = data['dealPrice']
                # co.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
                try:
                    co.total_price = int(int(co.avg_price)*float(co.area))
                except:
                    co.total_price = None
                co.url = comm_detail_url
                co.insert_db()

    # 第二种解析模式
    def comm_detail_new(self, comm_url_list, city):
        for comm_url in comm_url_list:
            com_url = city.replace('/xiaoqu/', comm_url)
            try:
                res = requests.get(url=com_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('source={}, 请求失败 url={} e={}'.format('中原地产', com_url, e))
                continue
            self.parse(res, com_url)

    def parse(self, res, com_url):
        co = Base(source)
        co.url = com_url
        tree = etree.HTML(res.text)
        # 小区名称
        district_name = tree.xpath("//dl[@class='fl roominfor']/dd/h2/text()")[0].replace(' ', '')
        co.district_name = district_name
        # 城市
        city = tree.xpath("/html/body/div[3]/div/a[1]/text()")[0].replace('中原地产', '')
        co.city = city
        # 区域
        region = tree.xpath("/html/body/div[3]/div/a[3]/text()")[0].replace('小区', '')
        co.region = region
        info_list = tree.xpath("//div[@class='tablerecord-list']/div[@class='tablerecond-item']")
        for info in info_list:

            # 室数
            try:
                room_type = info.xpath("./a/span[1]/text()")[0]
                room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
                co.room = room
            except:
                co.room = None
            try:
                # 厅数
                room_type = info.xpath("./a/span[1]/text()")[0]
                hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
                co.hall = hall
            except:
                co.hall = None
            # 朝向
            try:
                direction = info.xpath("./a/span[2]/text()")[0].replace(' ', '').replace('\n', '').replace('\t', '')
                co.direction = direction
            except:
                co.direction = None
            try:
                # 面积
                area = info.xpath('./a/span[3]/text()')[0].replace('平', '')
                area = round(float(area), 2)
                co.area = area
            except:
                co.area = None
            # 交易时间
            try:
                trade_date = info.xpath('./a/span[4]/text()')[0]
                t = time.strptime(trade_date, "%Y/%m/%d")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                co.trade_date = co.local2utc(datetime.datetime(y, m, d))
            except:
                co.trade_date = None
            # # 总价
            # try:
            #     total_price = info.xpath("./a/span[5]/text()")[0]
            #     total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
            #     co.total_price = total_price
            # except:
            #     co.total_price = None
            # 均价
            try:
                avg_price = info.xpath("./a/span[6]/text()")[0]
                avg_price = int(avg_price.replace('元/平', ''))
                co.avg_price = avg_price
            except:
                co.avg_price = None
            # 总价
            try:
                co.total_price = int(int(co.avg_price)*float(co.area))
            except:
                co.total_price = None
            co.insert_db()
