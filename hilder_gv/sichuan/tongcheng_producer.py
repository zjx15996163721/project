import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
import pika
import json
import threading
from retry import retry
log = LogHandler('58tongcheng')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['sichuan']

sichuan_city_list = ['成都', '绵阳', '宜宾', '自贡', '攀枝花',
                 '广元', '乐山', '南充', '泸州', '资阳',
                 '内江', '达州', '巴中', '遂宁', '眉山',
                 '德阳', '广安', '雅安', '阿坝州','甘孜州','凉山州']



class TongCheng:

    def __init__(self):
        self.headers = {
            'cookie': 'f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; commontopbar_ipcity=changningx%7C%E9%95%BF%E5%AE%81%7C0; id58=c5/nn1wXQ3A0wzemGmI5Ag==; 58tj_uuid=ac20c541-e164-40e1-9718-be72a9452a47; new_uv=1; utm_source=; spm=; init_refer=; als=0; xxzl_deviceid=1JOCn9ahzkV496HWqiDmLtPpyMp%2FqLfDRox4ARmC2AAe3nOLYPtz7J6sLdUh2EYu; new_session=0; f=n; JSESSIONID=54D1B5AD360417F8F11B455DB234A22B; Hm_lvt_ae019ebe194212c4486d09f377276a77=1545037907,1545037957,1545037977,1545038822; Hm_lpvt_ae019ebe194212c4486d09f377276a77=1545040060; xzfzqtoken=Kk6eVz1jaZJhhM2mlrEeLm3pRRja69vQOWkFfyBjoRgM7c%2B%2FK%2FxBNFJd%2F4Yz1K9Sin35brBb%2F%2FeSODvMgkQULA%3D%3D',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = [
            'https://cd.58.com/xiaoqu/?PGTID=0d00000c-0000-03f6-f953-cb7fb94917aa&ClickID=1',
            'https://mianyang.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://yb.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://zg.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://panzhihua.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://guangyuan.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ls.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://nanchong.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://luzhou.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://zy.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://scnj.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://dazhou.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://bazhong.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://suining.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ms.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://deyang.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ga.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ya.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ab.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://ganzi.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
            'https://liangshan.58.com/xiaoqu/?PGTID=0d00000c-0000-0e34-3579-331446a67768&ClickID=1',
        ]

    def start(self):
        for url in self.start_url:
            threading.Thread(target=self.start_crawler, args=(url, )).start()

    def start_crawler(self, url):
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     print(e)
        #     return
        r = self.send_url(url)
        tree = etree.HTML(r.text)
        region_info_list = tree.xpath('//div[@class="filter-wrap"]/dl[1]/dd/a')
        for region_info in region_info_list[1:]:
            region_id = region_info.xpath('./@value')[0]
            region_url = re.search('(https://.*?\.58\.com/xiaoqu/)', url, re.S | re.M).group(1) + region_id + '/pn_1/'
            total_page = self.get_max_page(region_url)
            if total_page:
                for page in range(1, int(total_page) + 1):
                    page_url = re.search('(https://.*?\.58\.com/xiaoqu/\d+/pn_)', region_url, re.S | re.M).group(1) + str(page) + '/'
                    self.get_all_url(page_url)

    def get_max_page(self, url):
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     print(e)
        #     return
        r = self.send_url(url)
        try:
            total_page = re.search('totalPage = (\d+);', r.text, re.S | re.M).group(1)
            return total_page
        except Exception as e:
            print(e)
            return

    def get_all_url(self, page_url):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        channel = connection.channel()
        # try:
        #     r = requests.get(url=page_url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error(e)
        #     return
        r = self.send_url(page_url)
        tree = etree.HTML(r.text)
        url_info_list = tree.xpath('//div[@class="content-side-left"]/ul/li')
        for info in url_info_list:
            url = info.xpath('./div[2]/h2/a/@href')[0]
            channel.queue_declare(queue='58tongcheng')
            channel.basic_publish(exchange='',
                                  routing_key='58tongcheng',
                                  body=json.dumps(url))
            log.info('放队列 {}'.format(url))

    @retry(delay=2,logger=log)
    def send_url(self,url):
        res = requests.get(url=url, headers=self.headers, proxies=p)
        return res


if __name__ == '__main__':

    tongcheng = TongCheng()
    tongcheng.start()

