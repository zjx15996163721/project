import requests
import re
from ceic.country import country
from dateutil import parser
from lib.mongo import Mongo
import random
import yaml
from lib.log import LogHandler

m = Mongo('192.168.0.235')
connect = m.connect

setting = yaml.load(open('config.yaml'))
db_name = setting['CEIC']['mongo']['db']
State_indicators_name = setting['CEIC']['mongo']['State_indicators']
State_indicators_details_name = setting['CEIC']['mongo']['State_indicators_details']
log = LogHandler('CEIC')

proxy = [{"https": "https://192.168.0.96:4234"},
         {"https": "https://192.168.0.93:4234"},
         {"https": "https://192.168.0.90:4234"},
         {"https": "https://192.168.0.94:4234"},
         {"https": "https://192.168.0.98:4234"},
         {"https": "https://192.168.0.99:4234"},
         {"https": "https://192.168.0.100:4234"},
         {"https": "https://192.168.0.101:4234"},
         {"https": "https://192.168.0.102:4234"},
         {"https": "https://192.168.0.103:4234"}, ]


class CEIC:
    """
    列表页面所有种类和信息
    """

    def __init__(self):
        self.countries_url = 'https://www.ceicdata.com/zh-hans/countries'

    def crawler(self):

        while True:
            try:
                proxy_ = proxy[random.randint(0, 9)]
                res = requests.get(url=self.countries_url, proxies=proxy_)
                if res.status_code == 200:
                    break
            except Exception as e:
                log.info('请求出错，url={}，proxy={}，'.format(self.countries_url, proxy_), e)

        # print(res.content.decode())
        country_list = []
        for url in re.findall('<a href="(/zh-hans/country/.*?)"', res.content.decode(), re.S | re.M):
            country_list.append('https://www.ceicdata.com' + url)

        for i in country_list:
            self.crawler_list_page(i)

    def crawler_list_page(self, url):
        # print('url={}'.format(url))
        while True:
            try:
                proxy_ = proxy[random.randint(0, 9)]
                res = requests.get(url=url, proxies=proxy_)
                if res.status_code == 200:
                    break
            except Exception as e:
                log.info('请求出错，url={}，proxy={}，'.format(self.countries_url, proxy_), e)
        html_str = res.content.decode()
        countryName = re.search('<h1 class="datapage-header">(.*?)</h1>', html_str, re.S | re.M).group(1)
        countryEnName = country[countryName]
        for info in re.findall('<tr class="datapage-table-row " >.*?</tr>', html_str, re.S | re.M):
            indexCategory = re.search('<td class="name-cell".*?data-th="(.*?)"', info, re.S | re.M).group(1)
            indexEnName = re.search('<a href="/.*?/.*?/.*?/(.*?)"', info, re.S | re.M).group(1)
            indexName = re.search('<a href="/.*?/.*?/.*?/.*?".*?title="(.*?)">', info, re.S | re.M).group(1)

            # 时间格式化
            start_time = re.search('范围.*?<p>(.*?)-.*?</p>', info, re.S | re.M).group(1)
            indexStart = parser.parse(start_time).strftime('%Y-%m')
            end_time = re.search('范围.*?<p>.*?-(.*?)</p>', info, re.S | re.M).group(1)
            indexEnd = parser.parse(end_time).strftime('%Y-%m')

            indexFrequency = re.search('frequency.*?data-value="(.*?)">', info, re.S | re.M).group(1)
            indexUnit = re.search('data-th="单位".*?<p>(.*?)</p>', info, re.S | re.M).group(1)
            indexUpdate = re.search('范围.*?<small>于(.*?)更新</small>', info, re.S | re.M).group(1)

            url = re.search('<a href="(.*?)"', info, re.S | re.M).group(1)

            # collection = connect['test']['State_indicators']
            collection = connect[db_name][State_indicators_name]
            data = {
                'countryName': countryName,
                'countryEnName': countryEnName,
                'indexCategory': indexCategory,
                'indexEnName': indexEnName,
                'indexName': indexName,
                'indexStart': indexStart,
                'indexEnd': indexEnd,
                'indexFrequency': indexFrequency,
                'indexUnit': indexUnit,
                'indexUpdate': indexUpdate,
                'url': 'https://www.ceicdata.com' + url
            }
            collection.update_one({'countryEnName': countryEnName, 'indexEnName': indexEnName}, {'$set': data}, True)
        log.info('{}国家已经结束'.format(countryName))
