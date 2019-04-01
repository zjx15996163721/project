import requests
import re
from lib.log import LogHandler
from lxml import etree
import pika
import json
import yaml
import threading
log = LogHandler('链家在线')
url = 'https://sh.lianjia.com/'
setting = yaml.load(open('config_local.yaml'))


class LianjiaProducer:

    def __init__(self, proxies):
        self.headers = {
            'Cookie': 'TY_SESSION_ID=d4338070-8794-470d-b4ec-2ad3387344c0; lianjia_uuid=602795b2-d2ac-441b-8c39-e9d1f2f69c0b; _smt_uid=5bea30ce.66e4f57; _jzqc=1; UM_distinctid=1670aceae1de93-0bd892eb8bcfc4-162a1c0b-1fa400-1670aceae1e38a; _ga=GA1.2.605174491.1542074580; all-lj=8e5e63e6fe0f3d027511a4242126e9cc; _qzjc=1; _gid=GA1.2.796022824.1542787626; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1542074574,1542787625,1542890281; _jzqy=1.1542787625.1542890282.2.jzqsr=baidu|jzqct=l%E9%93%BE%E5%AE%B6%E5%9C%B0%E4%BA%A7.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6; _jzqckmp=1; lianjia_ssid=ec3232f7-b93a-46f5-9f2c-0a8e2c9677c3; _jzqa=1.360625764904573300.1542074575.1542890282.1542897776.12; CNZZDATA1253477573=1618843455-1542296122-%7C1542895652; CNZZDATA1254525948=607236343-1542296853-%7C1542899223; CNZZDATA1255633284=949921736-1542293817-%7C1542898946; CNZZDATA1255604082=1666070452-1542292506-%7C1542897751; select_city=110000; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1542900864; _qzja=1.567450687.1542297093271.1542644069959.1542899998599.1542900826998.1542900865161.0.0.0.30.6; _qzjb=1.1542899998599.12.0.0.0; _qzjto=12.1.0; _jzqb=1.21.10.1542897776.1; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.proxies = proxies
        self.count = 0

    def start_crawler(self):
        response = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        html = response.text
        city_list_html = re.search('city-tab".*?</div></div></div>', html, re.S | re.M).group()
        city_a_html_list = re.findall('<a.*?</a>', city_list_html, re.S | re.M)
        city_dict = {}
        for i in city_a_html_list:
            city = re.search('<a.*?>(.*?)<', i, re.S | re.M).group(1)
            city_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
            if 'you' not in city_url and 'fang' not in city_url:
                city_dict[city] = city_url
        self.get_city_info(city_dict)

    def get_city_info(self, city_dict):
        for city in city_dict.items():
            threading.Thread(target=self.start_request, args=(city,)).start()

    def start_request(self, city_tuple):
        city_url = city_tuple[1] + 'xiaoqu/'
        city = city_tuple[0]
        try:
            response = requests.get(url=city_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求错误，source="{}",url="{}",e="{}"'.format('链家在线', city_url, e))
            return
        html = response.text
        self.get_page_list(html, city, city_url)

    def get_page_list(self, html, city, city_url):
        try:
            area_html = re.search('data-role="ershoufang".*?地铁', html, re.S | re.M).group()
            area_list_str = re.findall('<a.*?</a>', area_html, re.S | re.M)
        except:
            return
        for area_i in area_list_str:
            if 'ershoufang' in area_i:
                continue
            area_url = re.search('href="(.*?)"', area_i, re.S | re.M).group(1)
            region = re.search('<a.*?>(.*?)<', area_i, re.S | re.M).group(1)
            if 'http' in area_url:
                city_url_ = area_url
            else:
                city_url_ = city_url.replace('/xiaoqu/', '') + area_url
            max_page = self.get_page(city_url_)
            for i in range(1, max_page+1):
                url = city_url_ + 'pg' + str(i) + '/'
                self.get_page_url_list(url, city, region)

    def get_page(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 source={}, url={}, e={}'.format('链家在线', url, e))
            return
        try:
            num = re.search('共找到<span> (.*?) </span>个小区', r.text, re.S | re.M).group(1)
            max_page = int(int(num)/30) + 1
            return max_page
        except Exception as e:
            log.error(e)
            return 1

    def get_page_url_list(self, page_url, city, region):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port'], heartbeat=0))
        channel = connection.channel()
        try:
            response = requests.get(url=page_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 source={}, url={}, e={}'.format('链家在线', page_url, e))
            return
        tree = etree.HTML(response.text)
        url_list = tree.xpath("//ul[@class='listContent']/li")
        for i in url_list:
            link = i.xpath("./div[1]/div[1]/a[1]/@href")[0]
            xiaoqu_id = re.search('.*?xiaoqu/(.*?)/', link, re.S | re.M).group(1)
            half_url = re.search('(.*?)/xiaoqu', link, re.S | re.M).group(1)
            final_url = half_url + '/chengjiao/pg1c' + xiaoqu_id + '/'
            try:
                r = requests.get(url=final_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败, source={}, 没有更多小区成交 url={}, e={}'.format('链家在线', final_url, e))
                continue
            try:
                maxpage = re.search('"totalPage":(\d+),', r.text, re.S | re.M).group(1)
            except Exception as e:
                log.error('没有页码, source={}, url={}, e={}'.format('链家在线', final_url, e))
                continue
            for page in range(1, int(maxpage) + 1):
                detail_url = half_url + '/chengjiao/pg' + str(page) + 'c' + xiaoqu_id + '/'
                data = {
                    'link': detail_url,
                    'city': city,
                    'region': region
                }
                # self.parse_to235(data)
                # 数据入43的队列
                self.count += 1
                print(self.count)
                channel.queue_declare(queue='lianjia')
                channel.basic_publish(exchange='',
                                      routing_key='lianjia',
                                      body=json.dumps(data))
                log.info('放队列 {}'.format(data))

    def parse_to235(self, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port'], heartbeat=0))
        channel = connection.channel()
        # channel.queue_declare(queue='lianjia')

        url = data['link']
        city = data['city']
        region = data['region']
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error(e)
            return
        tree = etree.HTML(r.text)
        detail_url_list = tree.xpath("//ul[@class='listContent']/li")
        for detail in detail_url_list:
            detail_url = detail.xpath("./div/div[@class='title']/a/@href")[0]
            info = {
                 'link': detail_url,
                 'city': city,
                 'region': region
            }

            self.count += 1
            print(self.count)
            channel.queue_declare(queue='lianjia')
            channel.basic_publish(exchange='',
                                  routing_key='lianjia',
                                  body=json.dumps(info))
            log.info('放队列 {}'.format(info))
        connection.close()

