import re
import math
from lib.proxy_iterator import Proxies
import requests
from lxml import etree
from lib.log import LogHandler
import json

import pika

log = LogHandler(__name__)
source = 'realtor'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673))
p = Proxies()


class Realtor:
    def __init__(self, proxy):
        self.start_url = 'http://www.realtor.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36', }
        self.proxy = proxy

    def start_crawler(self):
        res = requests.get(self.start_url, headers=self.headers, proxies=self.proxy)
        html = etree.HTML(res.content.decode())
        cate_list = html.xpath('//*[@id="footer-seo-linking-modules"]/div/div/div[1]//ul/li')
        self.markets_cate(cate_list)

    def markets_cate(self, cate_list):
        """
        主要地区分类
        :return:
        """
        for cate in cate_list:
            cate_url = cate.xpath('./a/@href')[0]
            # self.sale_fetch(cate_url)
            self.sold_fetch(cate_url)
            # self.rent_fetch(cate_url)

    def proxy_request(self, url):
        """
        代理请求
        :param url:
        :return:
        """
        while True:
            try:
                resp = requests.get(url, headers=self.headers, proxies=self.proxy)
                if resp.status_code == 200:
                    con = resp.content.decode()
                    if 'Your IP address has been blocked' in con:
                        log.error('ip is banned,url={}'.format(url))
                        # todo 切换ip
                        requests.get('http://ip.dobel.cn/switch-ip', headers=self.headers, proxy=self.proxy)
                    else:
                        return con
                else:
                    log.error('{}请求失败'.format(url))
                    # todo 切换ip
                    requests.get('http://ip.dobel.cn/switch-ip', headers=self.headers, proxy=self.proxy)
            except Exception as e:
                log.error('{}请求失败={}'.format(url, e))
                # todo 切换ip
                requests.get('http://ip.dobel.cn/switch-ip', headers=self.headers, proxy=self.proxy)

    def page_divide(self, cate_url):
        """
        分页
        :param cate_url:
        :return:
        """
        res = self.proxy_request(cate_url)
        try:
            pagestring = re.search('Found (.*?) matching properties', res).group(1)
        except:
            return None
        count = int(pagestring.replace(',', ''))
        page = math.ceil(count / 48)
        return page

    def sale_fetch(self, cate_url):
        """
        挂牌销售
        :param cate_url:
        :return:
        """
        page = self.page_divide(cate_url)
        if page is None:
            return
        url_list = []
        for i in range(1, int(page) + 1):
            url = cate_url + '/pg-' + str(i)
            pageres = self.proxy_request(url)
            html = etree.HTML(pageres)
            house_list = html.xpath("//li[@class='component_property-card js-component_property-card js-quick-view']")
            for house in house_list:
                house_id = 'M' + house.xpath('./@data-propertyid')[0]
                detail_url = 'http://www.realtor.com/property-overview/' + house_id
                url_list.append(detail_url)
                if len(url_list) == 24:
                    rabbit = connection.channel()
                    rabbit.queue_declare(queue='listprice')
                    rabbit.basic_publish(exchange='', routing_key='listprice', body=json.dumps(url_list))
                    print('list_price放入队列')
                    url_list.clear()

    def sold_fetch(self, url):
        """
        已售出
        :param url:
        :return:
        """
        sold_url = url.replace('realestateandhomes-search', 'soldhomeprices')
        page = self.page_divide(sold_url)
        if page is None:
            return
        url_list = []
        for i in range(1, int(page) + 1):
            url = sold_url + '/pg-' + str(i)
            pageres = self.proxy_request(url)
            html = etree.HTML(pageres)
            house_list = html.xpath("//li[@class='component_property-card js-component_property-card ']")
            for house in house_list:
                house_id = 'M' + house.xpath("./@data-propertyid")[0]
                detail_url = 'http://www.realtor.com/property-overview/' + house_id
                url_list.append(detail_url)
                if len(url_list) == 24:
                    rabbit = connection.channel()
                    rabbit.queue_declare(queue='soldprice')
                    rabbit.basic_publish(exchange='', routing_key='soldprice', body=json.dumps(url_list))
                    print('soldprice放入队列')
                    url_list.clear()

    def rent_fetch(self, url):
        """
        出租房
        :param url:
        :return:
        """
        rent_url = url.replace('realestateandhomes-search', 'apartments')
        page = self.page_divide(rent_url)
        if page is None:
            return
        url_list = []
        for i in range(1, int(page) + 1):
            url = rent_url + '/pg-' + str(i)
            res = self.proxy_request(url)
            html = etree.HTML(res)
            house_list = html.xpath("//li[@class='component_property-card js-component_property-card ']")
            for house in house_list:
                house_id = 'M' + house.xpath("./@data-propertyid")[0]
                detail_url = 'http://www.realtor.com/property-overview/' + house_id
                url_list.append(detail_url)
                if len(url_list) == 24:
                    rabbit = connection.channel()
                    rabbit.queue_declare(queue='rentprice')
                    rabbit.basic_publish(exchange='', routing_key='rentprice', body=json.dumps(url_list))
                    print('rentprice放入队列')
                    url_list.clear()
if __name__ == '__main__':
    s = Realtor(next(p))
    s.start_crawler()