import requests
import re
# from deal_price_info import Comm
from BaseClass import Base
import time
import datetime
from lib.log import LogHandler

log = LogHandler('太屋网')


class Taiwuwang(object):

    def __init__(self, proxies):
        self.headers = {
            'Cookie': 'ASP.NET_SessionId=eogy5yjapzf2rg5q4nli2ycn; fangtuvid=6f613aff1c07451db55f277844c7b02d; fangtusid=6f613aff1c07451db55f277844c7b02d; clientId=be1979217507459d912744b852c53e41; UM_distinctid=16737260c1814b-083835ae2b313c-162a1c0b-1fa400-16737260c199a0; CNZZDATA1264983585=1856289162-1542818499-%7C1542818499; Hm_lvt_f1409f1a5fbfc4cf6d3c734789a6b94b=1542818504; Hm_lpvt_f1409f1a5fbfc4cf6d3c734789a6b94b=1542818504',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.url = 'http://www.taiwu.com/building/'
        self.proxies = proxies

    def start_crawler(self):
        page = self.get_all_page()
        for i in range(1, int(page)+1):
            url = 'http://www.taiwu.com/building/cp' + str(i) + '/'
            try:
                res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败，source="{}",url="{}",e="{}"'.format('太屋网', url, e))
                continue
            self.get_detail(res)

    def get_detail(self, res):
        try:
            all_info = re.search('<ul class="fang-list">.*?</ul>', res.content.decode(), re.S | re.M).group(0)
        except Exception as e:
            log.error('获取小区信息失败，source="{}", e="{}"'.format('太屋网', e))
            return
        for k in re.findall('<li>.*?</li>', all_info, re.S | re.M):
            # 区域
            region = re.search('<div class="adds">.*?<a href="/building/.*?/">(.*?)</a>', k, re.S | re.M).group(1)
            # 小区ID
            building_id = re.search('<a href="/building/(.*?)/', k, re.S | re.M).group(1)
            detail_url = "http://www.taiwu.com/Building/GetHouseExchange/"
            payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"buildingId\"\r\n\r\n" + building_id + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pageIndex\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n5000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
            headers = {
                'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                'Cache-Control': "no-cache",
            }
            try:
                response = requests.request("POST", detail_url, data=payload, headers=headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败，source="{}",id="{}",e="{}"'.format('太屋网', building_id, e))
                continue
            self.parse(response, region)

    def parse(self, response, region):
        source = '太屋网'
        city = '上海'
        try:
            result_json = response.json()
        except Exception as e:
            log.error('无法序列化，source="{}",e="{}"'.format('太屋网', e))
            return
        data_list = result_json['data']
        for j in data_list:
            c = Base(source)
            # 城市
            c.city = city
            # 区域
            c.region = region
            # 室
            c.room = int(j['RoomCount'])
            # 厅
            c.hall = int(j['HollCount'])
            # 小区名称
            c.district_name = j['BuildingName']
            # 面积
            c.area = round(float(j['BldArea']), 2)
            # 朝向
            c.direction = j['Directed']
            # 所在楼层
            c.floor = int(j['Floor'])
            # 总楼层
            c.height = int(j['FloorCount'])
            # 交易日期
            trade_date = j['ExDate']
            trade_date_ = int(re.search('(\d+)', trade_date).group(1))
            t = time.localtime(int(trade_date_ / 1000))
            y = t.tm_year
            m = t.tm_mon
            d = t.tm_mday
            c.trade_date = c.local2utc(datetime.datetime(y, m, d))
            # 总价
            c.total_price = int(j['ExPrice'])
            # 均价
            try:
                c.avg_price = int(round(c.total_price / c.area, 2))
            except:
                c.avg_price = None
            # # 总价
            # try:
            #     c.total_price = int(int(c.avg_price)*float(c.area))
            # except:
            #     c.total_price = None
            c.insert_db()

    def get_all_page(self):
        r = requests.get(url=self.url, headers=self.headers, proxies=self.proxies)
        page = re.search("pagecount:(\d+),", r.text, re.S | re.M).group(1)
        return page

