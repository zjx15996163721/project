import requests
import json
from lib.bloom_filter import BloomFilter
from lib.rabbitmq import Rabbit
import re
from lxml import etree
import yaml
from article import Article
import datetime
import time
import random
import pika
from article_img.qiniu_fetch import qiniufetch
from lib.log import LogHandler

log = LogHandler('wangyi')
setting = yaml.load(open('config_local.yaml'))

class Wangyi:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36",
            # "Cookie": "TEMP_USER_ID=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiI1YWYxNDk5OTY4ZDYzIiwidGltZSI6MTUyNTc2MjQ1N30.yT2cDnBOA7Zj9lFxI52f064z6zI4zxPv78HWjvXvwyc; city_redirected=2; prov=cn021; city=021; weather_city=sh; region_ip=116.247.70.x; region_ver=1.2; userid=1525762465015_d0klfz8748; Hm_lvt_2618c9646a4a7be2e5f93653be3d5429=1525762465; Hm_lpvt_2618c9646a4a7be2e5f93653be3d5429=1525762465; ifh_site=3066%2C"
        }
        self.start_url = "http://sh.house.163.com/news/"
        self.proxies = [{"http": "http://192.168.0.96:3234"},
                        {"http": "http://192.168.0.93:3234"},
                        {"http": "http://192.168.0.90:3234"},
                        {"http": "http://192.168.0.94:3234"},
                        {"http": "http://192.168.0.98:3234"},
                        {"http": "http://192.168.0.99:3234"},
                        {"http": "http://192.168.0.100:3234"},
                        {"http": "http://192.168.0.101:3234"},
                        {"http": "http://192.168.0.102:3234"},
                        {"http": "http://192.168.0.103:3234"}, ]
        self.bf = BloomFilter(host=setting['redies_host'],
                              port=setting['redis_port'],
                              key='article_toutiao_test',
                              blockNum=1,
                              db=0, )



    def connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbitmq_host'],
                                                                    port=setting['rabbitmq_port']))
        self.channel = connection.channel()
        self.channel.exchange_declare('article', 'direct', durable=True)
        self.channel.queue_declare('wangyi_article', durable=True)
        self.channel.queue_bind(exchange='article',
                           queue='wangyi_article',
                           routing_key='white')

    def start_crawler(self):
        res = requests.get(self.start_url, headers=self.headers)
        res.encoding = 'gbk'
        html = etree.HTML(res.text)
        city_list = html.xpath("//div[@class='city']/a")
        for city in city_list:
            city_name = city.xpath("./text()")[0]
            city_url = city.xpath("./@href")[0]
            city_news_url = city_url+'news'
            self.city_news(city_name,city_news_url)

    def city_news(self,city_name,city_url):
        while True:
            try:
                proxy = self.proxies[random.randint(0,9)]
                news_res = requests.get(city_url, headers=self.headers,proxies=proxy)
                break
            except Exception as e:
                log.error(e)
                continue
        news_res.encoding = 'gbk'
        news_html = etree.HTML(news_res.text)
        try:
            cate_list = news_html.xpath("//div[@class='importent-news']")
        except Exception as e:
            log.info(e)
            return
        for cate in cate_list:
            cate_name = cate.xpath("./h2/a/text()")[0]
            news_list = cate.xpath("./ul/li")
            for news in news_list:
                url = news.xpath("./h3/a/@href")[0]
                if self.bf.is_contains(url):  # 过滤详情页url
                    log.info('bloom_filter已经存在{}'.format(url))
                    continue
                else:
                    self.bf.insert(url)
                    log.info('bloom_filter不存在，插入新的url:{}'.format(url))
                try:
                    desc = news.xpath("./div[@class='news-detail']/p/text()")[0]
                except:
                    desc = None
                article = Article('网易')
                article.url = url
                article.desc = desc
                article.city = city_name
                article.category = cate_name
                message = json.dumps(article.to_dict())

                disconnected = True
                while disconnected:
                    try:
                        disconnected = False
                        self.channel.basic_publish(exchange='article',
                                                   routing_key='white',
                                                   body=message,
                                                   properties=pika.BasicProperties(delivery_mode=2))
                        log.info('已经放入队列')
                    except Exception as e:
                        log.error(e)
                        self.connect()
                        disconnected = True