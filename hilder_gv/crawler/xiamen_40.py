"""
url = http://fdc.xmtfj.gov.cn:8001/search/commercial_property
city :  厦门
CO_INDEX : 40
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm
import requests
import json

co_index = 40


class Xiamen(Crawler):
    def __init__(self):
        self.start_url = "http://fdc.xmtfj.gov.cn:8001/search/commercial_property"
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        for i in range(1, 10000):
            formdata = {
                "currentpage": i,
                "pagesize": 20,
            }
            try:
                res = requests.post("http://fdc.xmtfj.gov.cn:8001/home/Getzslp", data=formdata, headers=self.headers)
                con = json.loads(res.text)
                body = con['Body']
                info_dict = json.loads(body)['bodylist']
                for i in info_dict:
                    comm = Comm(co_index)
                    comm.co_name = i['XMMC']
                    comm.co_id = i['TRANSACTION_ID']
                    comm.co_address = i['XMDZ']
                    comm.co_pre_sale = i['YSXKZH']
                    comm.co_all_house = i['PZTS']
                    comm.co_build_size = i['PZMJ']
                    comm.co_area = i['XMDQ']
                    comm.co_pre_date = i['GETDATE']
                    comm.insert_db()
            except Exception as e:
                print('小区错误，co_index={},url={},data'.format(co_index, 'http://fdc.xmtfj.gov.cn:8001/home/Getzslp',
                                                            formdata), e)


if __name__ == '__main__':
    xiamen = Xiamen()
    xiamen.start_crawler()
