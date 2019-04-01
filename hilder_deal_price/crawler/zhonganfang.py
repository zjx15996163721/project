"""
    中安房网址失效，打不开，这不做了
"""
import requests
import re
from deal_price_info import Comm
from retry import retry
import time, datetime
from lib.log import LogHandler

log = LogHandler('中安房')
url = 'http://deal.zaf.cc/'


class Zhonganfang():
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    @retry(tries=3)
    def start_crawler(self):
        response = requests.get(url, headers=self.headers)
        html = response.text
        page = re.search('下一页.*?page=(.*?)"', html, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            all_page_url = 'http://deal.zaf.cc/?page=' + str(i)
            try:
                result = requests.get(all_page_url, headers=self.headers)
                content = result.text
                comm_list = re.findall('<li class="list-li">.*?</li>', content, re.S | re.M)
                self.get_comm_info(comm_list, all_page_url)
            except Exception as e:
                log.error('请求错误，source={},url="{}",e="{}"'.format('中安房', all_page_url, e))
                raise

    def get_comm_info(self, comm_list, all_page_url):
        for i in comm_list:
            try:
                comm = Comm('中安房')
                comm.city = '合肥'
                comm.district_name = re.search('zaf-nowrap.*?>(.*?)<', i, re.S | re.M).group(1).strip()
                trade_date = re.search('zaf-fblue">(.*?)<', i, re.S | re.M).group(1).strip()
                if trade_date:
                    t = time.strptime(trade_date, "%Y-%m-%d")
                    y = t.tm_year
                    m = t.tm_mon
                    d = t.tm_mday
                    comm.trade_date = datetime.datetime(y, m, d)
                total_price = re.search('list-right-data.*?<span.*?>(.*?)<', i, re.S | re.M).group(1).strip()
                comm.total_price = int(re.search('(\d+)', total_price, re.S | re.M).group(1)) * 10000
                info = re.search('list-details-area.*?<span.*?>(.*?)<', i, re.S | re.M).group(1).strip()
                area = info.split('　')[0].replace('㎡', '')
                if area:
                    area = float(area)
                    comm.area = round(area, 2)
                try:
                    room_type = info.split('　')[1]
                except Exception as e:
                    room_type = None
                try:
                    comm.room = int(re.search('(\d)室', room_type, re.S | re.M).group(1))
                except Exception as e:
                    comm.room = 0
                try:
                    comm.hall = int(re.search('(\d)厅', room_type, re.S | re.M).group(1))
                except Exception as e:
                    comm.hall = None
                try:
                    comm.toilet = int(re.search('(\d)卫', room_type, re.S | re.M).group(1))
                except Exception as e:
                    comm.toilet = None
                try:
                    avg_price = info.split('　')[2]
                    comm.avg_price = int(re.search('(\d+)', avg_price, re.S | re.M).group(1))
                except Exception as e:
                    comm.avg_price = None
                info_2 = re.search('list-details-area.*?<span.*?<span>(.*?)<', i, re.S | re.M).group(1).strip()
                comm.direction = info_2.split('　')[0]
                try:
                    comm.fitment = info_2.split('　')[1]
                except Exception as e:
                    comm.fitment = None
                info_3 = re.search('list-details-address1.*?<span>(.*?)<', i, re.S | re.M).group(1).strip()
                comm.region = info_3.split('　')[0].strip()
                comm.insert_db()
            except Exception as e:
                log.error('解析错误，source={},url="{}",e="{}"'.format('中安房', all_page_url, e))
