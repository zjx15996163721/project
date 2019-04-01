import requests
from lib.proxy_iterator import Proxies
from lxml import etree


p = Proxies()


class Lianjia:
    def __init__(self):
        # cro 21 小区均价 cro11 按成交量
        self.district_urls = ['https://sh.lianjia.com/xiaoqu/cro21/', 'https://sh.lianjia.com/xiaoqu/cro11/']
        # 新房成交
        # self.new_district_url = 'https://sh.fang.lianjia.com/loupan/'
        self.new_district_url = 'https://www.baidu.com'



    def crawler(self):
        pass

    def get_area(self):
        res = requests.get(url=self.new_district_url, proxies=p.get_one(proxies_number=7))
        # res = requests.get(url=self.new_district_url)

        html = etree.HTML(res.text)
        html.xpath('/html/body/div[2]/div[2]/ul/li')
        print(res.text)


if __name__ == '__main__':
    l = Lianjia()
    l.get_area()
