"""
url = http://zzx.zzfc.com/xy_ysxk_more.aspx#
city :  株洲
CO_INDEX : 201
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Building, House
import re, requests
from lib.log import LogHandler


co_index = '201'
city = '株洲'
log = LogHandler("zhuzhou")

class Zhuzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://zzx.zzfc.com/xy_ysxk_more.aspx#'
        self.headers={
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'X-AjaxPro-Method':'GETYSXKDS'
        }
        self.proxies = [{"http": "http://192.168.0.96:3234"},
                        {"http": "http://192.168.0.93:3234"},
                        {"http": "http://192.168.0.90:3234"},
                        {"http": "http://192.168.0.94:3234"},
                        {"http": "http://192.168.0.98:3234"},
                        {"http": "http://192.168.0.99:3234"},
                        {"http": "http://192.168.0.100:3234"},
                        {"http": "http://192.168.0.101:3234"},
                        {"http": "http://192.168.0.102:3234"},
                        {"http": "http://192.168.0.103:3234"}, ]
    def start_crawler(self):
        url = 'http://zzx.zzfc.com/ajaxpro/xy_ysxk_more,App_Web_mjeeodb-.ashx'
        for i in range(1,21):
            payload = "{\"pageNo\":"+str(i)+",\"pageSize\":30,\"rowcount\":589}"
            try:
                response = requests.post(url,data=payload,headers=self.headers)
                con = response.content.decode()
            except Exception as e:
                log.error('楼栋请求失败{}'.format(e))
                continue
            co_list = re.findall('\[\d+,.*?\d+\]',con)
            for comm in co_list:
                try:
                    sid = re.search('\[(\d+),',comm).group(1)
                    pid = re.search('",(\d+),',comm).group(1)
                    bu_url = 'http://zzx.zzfc.com/xy_bldg.aspx?pid='+pid+'&sid='+sid
                    bu_res = requests.get(bu_url,headers=self.headers)
                    bu_con = bu_res  .content.decode()
                    bu = Building(co_index)
                    bu.bu_id = sid
                    bu.bu_address = re.search('楼栋座落.*?">(.*?)&nbsp',bu_con,re.S|re.M).group(1)
                    bu.bu_pre_sale = re.search('预售证号.*?">(.*?)&nbsp',bu_con,re.S|re.M).group(1)
                    bu.bu_pre_sale_date = re.search('预售日期.*?">(.*?)&nbsp',bu_con,re.S|re.M).group(1)
                    bu.bu_all_house = re.search('套数.*?">(.*?)&nbsp',bu_con,re.S|re.M).group(1)
                    bu.insert_db()
                except Exception as e:
                    log.error("{}楼栋解析失败{}".format(comm,e))
                    continue
                ho_url = 'http://zzx.zzfc.com/ajaxpro/xy_housetag,App_Web_xg4ulr9n.ashx'
                data = "{\"m_key\":\"WWW_LPB_001\",\"m_param\":\""+sid+"\"}"
                headers={
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
                'X-AjaxPro-Method':'GETLPBDS'
        }
                try:
                    ho_res = requests.post(ho_url,data=data,headers=headers)
                    ho_con = ho_res.content.decode()
                except Exception as e:
                    log.error("房屋请求失败{}".format(e))
                    continue
                ho_list = re.findall('\["\d+.*?\d+\]',ho_con)
                for house in ho_list:
                    try:
                        ho = House(co_index)
                        ho.bu_id = sid
                        info_list = house.split(",")
                        ho.ho_name = info_list[4]
                        ho.ho_floor = re.search('(\d+)层',house).group(1)
                        ho.ho_build_size = info_list[-3]
                        ho.ho_true_size = info_list[-2]
                        ho.insert_db()
                    except Exception as e:
                        log.error("{}房屋解析错误{}".format(house,e))
                        continue



