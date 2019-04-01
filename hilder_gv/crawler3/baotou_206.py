"""
url = http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init
city :  包头
CO_INDEX : 206
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '206'
city_name = '包头'
log = LogHandler('包头')
# ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-pro.abuyun.com", "port": "9010",
#                                                      "user": "HRH476Q4A852N90P", "pass": "05BED1D0AF7F0715"}

class Baotou(Crawler):
    def __init__(self):
        self.start_url = 'http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        for i in range(1, 40):
            url = 'http://zfbzj.baotou.gov.cn/index.php?m=content&c=permit&a=init&page='+str(i)
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content.decode())
            temp_list = html.xpath("//tr/td[@align='left']/a")
            for temp in temp_list:
                try:
                    temp_url = temp.xpath("./@href")[0]
                    co_res = requests.get(temp_url,headers=self.headers)
                    content = co_res.content.decode()
                    co = Comm(co_index)
                    co.co_id = re.search('id=(\d+)',temp_url).group(1)
                    co.co_name = re.search('项 目 名 称.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_develops = re.search('开发建设单位.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_address = re.search('项 目 座 落.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_pre_sale = re.search('预销售许可证号.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_pre_sale_date = re.search('发证日期.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.insert_db()
                except Exception as e:
                    log.error("{}小区解析失败{}".format(temp_url,e))
                    continue




