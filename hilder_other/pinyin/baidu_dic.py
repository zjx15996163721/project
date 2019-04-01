import requests
import urllib.parse
import re
from pymongo import MongoClient
from lib.proxy_iterator import Proxies

p = Proxies()
proxies = p.get_one(proxies_number=7)

client = MongoClient('mongodb://goojia:goojia7102@114.80.150.196:27777')
collection = client['temp_seaweed_status0_ly']['pinyin']


class BaiduDictionary:
    def __init__(self):
        self.url = 'http://dict.baidu.com/s?device=pc&from=home&wd='

    def crawler(self, wd):
        r = requests.get(self.url + urllib.parse.quote(wd.encode()), proxies=proxies)
        info = re.search('<ul id="header-list">(.*?)</ul>', r.text, re.S | re.M).group(1)
        count = 0
        pinyin_list = []
        for i in re.findall('<b>(.*?)</b>', info, re.S | re.M):
            pinyin_list.append(i)
            count = count + 1
        collection.update({'word': wd}, {'$set': {
            'count': count,
            'pinyin_list': pinyin_list,
        }})


def main():
    b = BaiduDictionary()
    info = collection.find({'count': {'$exists': 0}})
    for i in info:
        try:
            print(i['word'])
            b.crawler(i['word'])
        except:
            print('继续跑')


if __name__ == '__main__':
    for i in range(10):
        print('11111')

