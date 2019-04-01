import requests
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
from lib.log import LogHandler
from lxml import etree
import time
import re
log = LogHandler('yibin')
p = Proxies()
p = p.get_one(proxies_number=1)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['sichuan']


class YinBin:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.start_url = [('prewebissue', 19), ('nowwebissue', 8)]

    def start_crawler(self):
        for i in self.start_url:
            for page in range(1, int(i[1])+1):
                url = 'http://sfgj.yibin.gov.cn/tt/ybxxzs/xmlpzs/' + i[0] + '.asp?page=' + str(page)
                try:
                    r = requests.get(url=url, headers=self.headers)
                except Exception as e:
                    log.error(e)
                    continue
                self.get_district(r)

    def get_district(self, r):
        r.encoding = 'gbk'
        tree = etree.HTML(r.text)
        info_list = tree.xpath('/html/body/table[3]/tr/td[2]/table[3]/tr/td/table[1]/tr')
        for info in info_list[1:]:
            url = 'http://sfgj.yibin.gov.cn/tt/ybxxzs/xmlpzs/' + info.xpath('./td[1]/a/@href')[0]
            name = info.xpath('./td[1]/a/text()')[0].replace(' ', '')
            self.get_detail(url, name)

    def get_detail(self, url, name):
        try:
            r = requests.get(url=url, headers=self.headers)
        except Exception as e:
            log.error(e)
            return
        r.encoding = 'gbk'
        tree = etree.HTML(r.text)
        try:
            address = re.search('项目位置.*?</div></td>.*?<td>(.*?)</td>', r.text, re.S | re.M).group(1)
        except:
            address = None
        info = tree.xpath('//table[4]/tr[2]/td[2]/a/@href')
        info2 = tree.xpath('//table[3]/tr[2]/td[2]/a/@href')
        if info:
            link = info[0]
            detail_url = 'http://sfgj.yibin.gov.cn/tt/ybxxzs/xmlpzs/' + link
            print(detail_url)
            self.final_parse(detail_url, name, address)
        elif info2:
            link = info2[0]
            detail_url = 'http://sfgj.yibin.gov.cn/tt/ybxxzs/xmlpzs/' + link
            print(detail_url)
            self.final_parse(detail_url, name, address)
        else:
            log.info('无详情信息')

    def final_parse(self, url, name, address):
        try:
            r = requests.get(url=url, headers=self.headers)
        except Exception as e:
            log.error(e)
            return
        r.encoding = 'gbk'
        finish_time = re.search('完工日期.*?</div></td>.*?<td>(.*?)</td>', r.text, re.S | re.M).group(1)
        data = {
            'source': 'yibin',
            'city': '宜宾',
            'region': None,
            'district_name': name,
            'complete_time': finish_time,
            'household_count': None,
            'estate_charge': None,
            'address': address,
            'estate_type2': '普通住宅',
            'url': url
        }
        if not crawler_collection.find_one({'source': 'yibin', 'city': '宜宾',
                                            'district_name': name, 'complete_time': finish_time,
                                            'address': address, 'url': url}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


if __name__ == '__main__':
    y = YinBin()
    y.start_crawler()

