"""
url = 'http://gs.czfdc.com.cn/newxgs/Pages/Ysz_List.aspx'
city :  常州
CO_INDEX : 166
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm
import requests
import json
from lib.log import LogHandler

co_index = '166'
city_name = '常州'
log = LogHandler('常州')

class Changzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://gs.czfdc.com.cn/newxgs/Pages/Code/Xjfas.ashx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer':
                'http://gs.czfdc.com.cn/newxgs/Pages/Ysz_List.aspx',
            'X-Requested-With':
                'XMLHttpRequest',
            'Cookie':'psaleID=; houseid=; psaleid=; wjbazt=; npsaleid=; ASP.NET_SessionId=0g0sjygk0ocwfwl4ro30cmeq; UM_distinctid=16435d646929e-0aee5df0642b02-444a012d-1fa400-16435d646942f2; CNZZDATA915400=cnzz_eid%3D1798897998-1529909745-%26ntime%3D1529909745'
        }
    def start_crawler(self):
        for i in range(1,478):
            data = {
                "method":"GetYszData",
                "page":str(i),
                "ysxkz":'',
                "kfs":'',
                "lpmc":''
            }
            res = requests.post(self.start_url,headers=self.headers,data=data)
            info = res.json()
            comm = json.loads(info)
            for detail in comm['Rows']:
                co = Comm(co_index)
                co.co_name = detail['PRJNAME']
                co.co_pre_sale = detail['PRENUM']
                co.area = detail['CZAREA']
                co.co_pre_sale_date = detail['PresaleCertificateDate']
                co.co_address = detail['BSIT']
                co.co_develops =  detail['NAME']
                co.co_build_size =  detail['YSROOMBAREA']
                co.co_all_house =  detail['YSROOMNUMS']
                co.insert_db()





