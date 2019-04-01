import pika
import json
import requests
from lib.log import LogHandler
from company_info import Company
from lib.proxy_iterator import Proxies

log = LogHandler('baidumap_consumer')
"""
字典格式:
dict = {
"city":"",
"region":"",
"search_word":""
"match_word":""
}
"""


class BaiduMapConsumer:
    def __init__(self, proxies):
        self.proxies = proxies
        self.source = 'baidumap'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.base_url = 'https://map.baidu.com/'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1',
            port=5673,
            heartbeat=0
        ))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='baidu_producer', durable=True)

    def start_consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            self.callback,
            queue='baidu_producer'
        )
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        address_dicts = json.loads(body.decode())
        for address_dict in address_dicts:
            self.send_first_url(address_dict)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_first_url(self, address_dict):
        """
        该函数主要目的是发送请求获取总页数
        :param address: 搜索的关键字
        :return:
        """
        search_word = address_dict['search_word']
        print(search_word)
        payload = {
            'from': 'webmap',
            'qt': 's',
            'wd': search_word,
            'pn': '0',
        }
        try:
            rest = requests.get(self.base_url, params=payload, headers=self.headers, proxies=self.proxies)
            res = rest.json()
            total = res['result']['total']
            if total == 0:
                log.error('{}该搜索关键字下没有对应的搜索结果'.format(address_dict))
                return
            total_pages = int(total / 10)
            print(total_pages)
        except Exception as e:
            log.error('{}请求没有成功,切换一下IP'.format(search_word))
            requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
            return
        self.send_page_url(address_dict, total_pages)

    def send_page_url(self, address_dict, total_pages):
        """
        该函数的主要目的是为了向每一页发送请求
        :param address: 搜索关键字
        :param total_pages: 该关键字下的总页数
        :return:
        """
        search_word = address_dict['search_word']
        for page_num in range(total_pages + 1):
            payload = {
                'from': 'webmap',
                'qt': 's',
                'wd': search_word,
                'pn': str(page_num)
            }
            try:
                rest = requests.get(self.base_url, params=payload, headers=self.headers, proxies=self.proxies)
                print(rest.url)
                res = rest.json()
            except Exception as e:
                log.error('{}请求没有成功,切换一下IP'.format(search_word))
                requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
                continue
            self.analyse_detail(res, address_dict, rest)

    def analyse_detail(self, res, address_dict, rest):
        try:
            contents = res['content']
        except:
            log.error('{}没有找到content这个字段'.format(rest.url))
            return
        for poi in contents[:10]:
            try:
                poi_address = poi['addr']
            except:
                log.error('{}没有addr这个字段'.format(rest.url))
                continue
            if address_dict['match_word'] not in poi_address:
                continue
            std_tag = poi['std_tag']
            di_tag = poi['di_tag']
            if std_tag is not None and di_tag is not None:
                tag = std_tag + di_tag
            elif std_tag is None and di_tag is not None:
                tag = di_tag
            elif std_tag is not None and di_tag is None:
                tag = std_tag
            else:
                tag = ''
            if '公司' in tag:
                try:
                    company_id = poi['primary_uid']
                    company = Company(company_id, self.source)
                except Exception as e:
                    log.error('{}中无法匹配到company_id'.format(rest.url))
                    continue
                company_name = poi['name']
                address = poi['addr']
                city = address_dict['city']
                region = address_dict['region']
                print(company_name,address,city,region)
                company.company_name = company_name
                company.address = address
                company.city = city
                company.region = region
                company.insert_db()


if __name__ == '__main__':
    p = Proxies()
    baidu = BaiduMapConsumer(proxies=next(p))
    baidu.start_consume()

