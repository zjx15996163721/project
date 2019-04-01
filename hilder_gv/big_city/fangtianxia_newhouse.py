import requests
from lxml import etree
from lib.proxy_iterator import Proxies
import re
from lib.log import LogHandler
import pika
import json
import threading
log = LogHandler('fangtianxia')
p = Proxies()
p = p.get_one(proxies_number=7)

top_city_list = ['上海', '北京', '广州', '深圳', '天津',
                 '无锡', '西安', '武汉', '大连', '宁波',
                 '南京', '沈阳', '苏州', '青岛', '长沙',
                 '成都', '重庆', '杭州', '厦门']


class FangTianXia:

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = [
            'http://sh.newhouse.fang.com/house/s/',
            'http://newhouse.fang.com/house/s/',
            'http://gz.newhouse.fang.com/house/s/',
            'http://sz.newhouse.fang.com/house/s/',
            'http://tj.newhouse.fang.com/house/s/',
            'http://wuxi.newhouse.fang.com/house/s/',
            'http://xian.newhouse.fang.com/house/s/',
            'http://wuhan.newhouse.fang.com/house/s/',
            'http://dl.newhouse.fang.com/house/s/',
            'http://nb.newhouse.fang.com/house/s/',
            'http://nanjing.newhouse.fang.com/house/s/',
            'http://sy.newhouse.fang.com/house/s/',
            'http://suzhou.newhouse.fang.com/house/s/',
            'http://qd.newhouse.fang.com/house/s/',
            'http://cs.newhouse.fang.com/house/s/',
            'http://cd.newhouse.fang.com/house/s/',
            'http://cq.newhouse.fang.com/house/s/',
            'http://hz.newhouse.fang.com/house/s/',
            'http://xm.newhouse.fang.com/house/s/',
        ]

    def start_crawler(self):
        for url in self.start_url:
            threading.Thread(target=self.start_request, args=(url,)).start()

    def start_request(self, url):
        r = requests.get(url=url, headers=self.headers, proxies=p)
        tree = etree.HTML(r.text)
        max_page_info = tree.xpath('//*[@id="sjina_C01_47"]/ul/li[2]/a[@class="last"]/@href')[0]
        max_page = re.search('/b9(\d+)/', max_page_info, re.S | re.M).group(1)
        for page in range(1, int(max_page)+1):
            page_url = url + 'b9' + str(page) + '/'
            self.get_url_list(page_url)

    def get_url_list(self, page_url):
        try:
            r = requests.get(url=page_url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        r.encoding = 'gbk'
        id_list = re.search("showhouseid':'(.*?)'}", r.text, re.S | re.M).group(1)
        new_house_id_list = id_list.split(',')
        name_list = []
        tree = etree.HTML(r.text)
        info_list = tree.xpath('//div[@id="newhouse_loupai_list"]/ul/li')
        for info in info_list:
            try:
                link = info.xpath('./div[1]/div[2]/div[1]/div[1]/a/@href')[0]
            except:
                continue
            name = re.search('//(.*?)\.fang', link, re.S | re.M).group(1)
            name_list.append(name)
        for i, j in zip(name_list, new_house_id_list):
            url = 'http://' + i + '.fang.com/house/' + j + '/housedetail.htm'
            self.add_queue(url)

    def add_queue(self, url):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        channel = connection.channel()
        data = {
            'url': url,
        }
        channel.queue_declare(queue='fangtianxia_newhouse')
        channel.basic_publish(exchange='',
                              routing_key='fangtianxia_newhouse',
                              body=json.dumps(data))
        log.info('放队列 {}'.format(data))
        connection.close()


if __name__ == '__main__':
    fangtianxia = FangTianXia()
    fangtianxia.start_crawler()
