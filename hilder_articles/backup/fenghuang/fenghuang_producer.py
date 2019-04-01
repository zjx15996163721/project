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

setting = yaml.load(open('config_local.yaml'))
log = LogHandler('fenghuang')

class Fenghuang:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36",
            "Cookie" : "TEMP_USER_ID=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiI1YWYxNDk5OTY4ZDYzIiwidGltZSI6MTUyNTc2MjQ1N30.yT2cDnBOA7Zj9lFxI52f064z6zI4zxPv78HWjvXvwyc; city_redirected=2; prov=cn021; city=021; weather_city=sh; region_ip=116.247.70.x; region_ver=1.2; userid=1525762465015_d0klfz8748; Hm_lvt_2618c9646a4a7be2e5f93653be3d5429=1525762465; Hm_lpvt_2618c9646a4a7be2e5f93653be3d5429=1525762465; ifh_site=3066%2C"
        }
        self.start_url = "http://sh.house.ifeng.com/news/wap"
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
        # self.rabbit = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'])
    def connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbitmq_host'],
                                                                    port=setting['rabbitmq_port']))
        self.channel = connection.channel()
        self.channel.exchange_declare('article', 'direct', durable=True)
        self.channel.queue_declare('fenghuang_article', durable=True)
        self.channel.queue_bind(exchange='article',
                           queue='fenghuang_article',
                           routing_key='black')

    def start_crawler(self):
        res = requests.get('http://house.ifeng.com/news',headers=self.headers)
        res.encoding = 'utf-8'
        html = etree.HTML(res.text)
        city_list = html.xpath("//ul[@id='city_hot1']/li/a")
        for city in city_list:
            city_name = city.xpath("./text()")[0]
            city_url = city.xpath("./@href")[0]
            city_id = city.xpath("./@siteid")[0]
            news_url = city_url + '/news'

            news_res = requests.get(news_url,headers=self.headers)
            news_res.encoding = 'utf-8'
            news_html = etree.HTML(news_res.text)
            cate_id_list = news_html.xpath("//ul[@id='newsNavScroll']/li[@cateid]")

            self.article_url_crawler(city_name,city_id,news_url,cate_id_list)


    def article_url_crawler(self,city_name,city_id,news_url,cate_id_list):
        post_url =  news_url + '/wap'
        count = 1
        while True:
            for i in cate_id_list:
                cate_id = i.xpath("./@cateid")[0]
                cate_name = i.xpath("./a/text()")[0]
                formdata = {
                    'pageid' : count,
                    'cateid' : cate_id,
                    'siteid' : city_id,
                    'type' : 2
                }
                # time.sleep(10)
                while True:
                    proxy = self.proxies[random.randint(0, 9)]
                    try:
                        res = requests.post(post_url,data=formdata,headers=self.headers,proxies=proxy)
                        json_dict = json.loads(res.text)
                        break
                    except Exception as e:
                        log.error(e)
                        continue

                if len(json_dict['data']['newslist']) == 0:
                    count = 1
                    continue
                else:
                    news_list = json_dict['data']['newslist']
                    for news_info in news_list:

                        try:
                            desc = news_info['desc']
                            url  = news_info['url']
                            keywords = news_info['keywords'].values()
                            keywords_list = []
                            for i in keywords:
                                keywords_list.append(i)
                        except:
                            continue
                        title_img_url = news_info['pic_url']
                        if self.bf.is_contains(url):  # 过滤详情页url
                            log.info('bloom_filter已经存在{}'.format(url))
                            continue
                        else:
                            self.bf.insert(url)
                            log.info('bloom_filter不存在，插入新的url:{}'.format(url))
                            new_title_img = qiniufetch(title_img_url, title_img_url)
                            article = Article('凤凰网')
                            article.url = url
                            article.desc = desc
                            article.tag = str(keywords_list)
                            article.title_img = new_title_img
                            article.city = city_name
                            article.category = cate_name
                            message = json.dumps(article.to_dict())

                            disconnected = True
                            while disconnected:
                                try:
                                    disconnected = False
                                    self.channel.basic_publish(exchange='article',
                                                          routing_key='black',
                                                          body=message,
                                                          properties=pika.BasicProperties(delivery_mode=2))
                                    log.info('已经放入队列')
                                except Exception as e:
                                    log.error(e)
                                    self.connect()
                                    disconnected = True

            count += 1

