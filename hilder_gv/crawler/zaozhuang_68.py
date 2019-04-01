from backup.comm_info import Comm
from backup.crawler_base import Crawler
import requests
import re

class Zaozhuang(Crawler):
    def __init__(self):
        self.co_index = 68
        self.url = ['http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_47_1_0_0_0_1.html?_=1521612625447',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_46_1_0_0_0_1.html?_=1521613169027',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_45_1_0_0_0_1.html?_=1521613204460',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_44_1_0_0_0_1.html?_=1521613221502',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_43_1_0_0_0_1.html?_=1521613242267',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_35_1_0_0_0_1.html?_=1521613265660',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_34_1_0_0_0_1.html?_=1521613292457',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_32_1_0_0_0_1.html?_=1521613316586',
                    'http://www.zzzzfdc.com.cn/site/p/2/productSetBlock_2_28_1_0_0_0_1.html?_=1521613333691']

    def start_crawler(self):
        for i in self.url:
            res = requests.get(url=i)
            html = res.content.decode()
            c = Comm(self.co_index)
            c.co_name = re.search('楼盘名称：</h5></td><td><span>(.*?)<', html, re.S | re.M).group(1)
            c.co_develops = re.search('开发建设单位：</h5></td><td><span>(.*?)</span>', html, re.S | re.M).group(1)
            c.co_address = re.search('项目位置：</h5></td><td><span>(.*?)</span>', html, re.S | re.M).group(1)
            c.co_build_size = re.search('建筑面积：</h5></td><td><span>(.*?)</span>', html, re.S | re.M).group(1)
            print(c.to_dict())
            c.insert_db()