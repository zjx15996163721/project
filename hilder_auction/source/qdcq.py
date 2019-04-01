"""
详情页是文章，不做了
"""
from lib.mongo import Mongo
import yaml
import requests

source = 'qdcq'  # 青岛产权交易所

setting = yaml.load(open('config.yaml'))
client = Mongo(setting['mongo']['host'], setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]


class QDCQ:
    def __init__(self):
        self.start_url = 'http://www.qdcq.net/article/xmpd/cqzrxxggpt/sszc/?'

    def start_crawler(self):
        list_url = self.get_all_page()
        for url in list_url:
            res = requests.get(url)
            print(res.text)
            break

    def get_all_page(self):
        return [self.start_url + str(i) for i in range(2, 44)]
