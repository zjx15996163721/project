import requests
import re
# from deal_price_info import Comm
from BaseClass import Base
import time
import datetime
from lib.log import LogHandler

url = 'http://sh.koofang.com/xiaoqu/pg1'
log = LogHandler('上海酷房网')


class Kufangwang():
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }
        self.proxies = proxies

    def start_crawler(self):
        num = 1
        while True:
            page_url = 'http://sh.koofang.com/xiaoqu/pg' + str(num)
            try:
                response = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败 source={} url={} e={}'.format('上海酷房网', page_url, e))
                num += 1
                continue
            html = response.text
            if '未找到符合所选条件的小区，建议您调整筛选条件再试试' in html:
                break
            else:
                self.get_comm_info(html)
                num += 1

    def get_comm_info(self, html):
        comm_info_html_list = re.findall('<div class="avail_conr">.*?</li>', html, re.S | re.M)
        for i in comm_info_html_list:
            comm = Base('上海酷房网')
            comm.city = '上海'
            comm.district_name = re.search('class="avail_cont".*?>(.*?)<', i, re.S | re.M).group(1).strip()
            comm.region = re.search('class="avail_district".*?<a.*?>(.*?)<', i, re.S | re.M).group(1).strip()
            comm_id = re.search('class="avail_cont".*?href="/xiaoqu/(.*?)\.html"', i, re.S | re.M).group(1)
            self.get_comm_detail(comm_id, comm)

    def get_comm_detail(self, comm_id, comm):
        comm_detail_url = 'http://webapi.koofang.com/api/Community/SaleRealtyDealViewPageList'
        payload = "{\"PublicRequest\":{\"AppVersion\":\"1\",\"SourceWay\":10},\"AreaCode\":\"B024\",\"PageNumber\":1,\"PageSize\":1000,\"Search\":{\"CommunityId\":\"" + comm_id + "\"}}"
        headers = {
            'Content-Type': "application/json",
        }
        try:
            response = requests.post(url=comm_detail_url, data=payload, headers=headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求错误,source="{}"，url="{}",data="{}",e="{}"'.format('上海酷房网', comm_detail_url, payload, e))
            return
        try:
            html = response.json()
        except Exception as e:
            log.error('序列化失败, source="{}",e="{}"'.format('上海酷房网', e))
            return
        comm_list = html['PageData']['Data']
        if not comm_list:
            return
        for i in comm_list:
            comm.room = int(i['RoomNum'])
            comm.hall = int(i['LivingRoomNum'])
            comm.direction = i['FaceOrientationName'].strip()
            trade_date = i['DealTime'].strip()
            if trade_date:
                t = time.strptime(trade_date, "%Y-%m-%d")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                comm.trade_date = comm.local2utc(datetime.datetime(y, m, d))
            comm.avg_price = int(i['DealUnitAmount'])
            # comm.total_price = int(i['DealAmount']) * 10000
            comm.area = float(i['ConstructionArea'])
            try:
                comm.total_price = int(int(comm.avg_price)*float(comm.area))
            except:
                comm.total_price = None
            comm.insert_db()

    # 这里取下一页的方法不好 不用看了
    def get_all_comm_url(self, url_page):
        try:
            response = requests.get(url=url_page, headers=self.headers, proxies=self.proxies)
            html = response.text
            try:
                page = re.search('next_page nextPage".*?xiaoqu/pg(.*?)"', html, re.S | re.M).group(1)
                print(page)
                page_url = 'http://sh.koofang.com/xiaoqu/pg' + str(page)
                self.get_comm_info(page_url)
                self.get_all_comm_url(page_url)
            except Exception as e:
                return
        except Exception as e:
            log.error('请求错误,source="{}"，url="{}",e="{}"'.format('上海酷房网', url_page, e))
