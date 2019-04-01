from lib.bloom_filter import BloomFilter
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
from article import Article
from lxml import etree
import requests
import json
import pika
import yaml
from itertools import cycle
from article_img.qiniu_fetch import qiniufetch

setting = yaml.load(open('config_local.yaml'))

m = MongoClient(setting['mongo_config']['config_host'], setting['mongo_config']['port'])
m.admin.authenticate(setting['mongo_config']['user_name'],setting['mongo_config']['password'] )
collection = m[setting['mongo_config']['config_db']][setting['mongo_config']['coll_list']]

bf = BloomFilter(host=setting['redies_host'],
                 port=setting['redis_port'],
                 key='article_test',
                 blockNum=1,
                 db=0, )

log = LogHandler(__name__)

connect = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbitmq_host'],
                                                            port=setting['rabbitmq_port'], ))


class CrawlerArticleListUrl:
    def __init__(self):
        self.proxy = Proxies()
    def crawler_url(self):
        all_dict = collection.find({})
        self.channel = connect.channel()
        for source_dict in cycle(all_dict):
            for info in source_dict['url']:
                url = info[1]
                city = info[0]
                for i in range(2):
                    try:
                        html = requests.get(url, timeout=10,proxies=next(self.proxy))
                        connect.process_data_events()# 代理
                        content = html.content.decode(source_dict['decode'])
                        if html.status_code == 200:
                            self.new_article(content, source_dict, city=city)
                            break
                    except Exception as e:
                        log.error("{}列表页访问失败{}".format(url, e))

    def new_article(self, html, source, city):
        page = etree.HTML(html)
        for single_article in page.xpath(source['single_article_rule']):
            article = Article(source['source'])
            try:
                article.title = single_article.xpath(source['title'])[0].strip()
            except:
                log.error('{}标题不符合xpath规则'.format(source['source']))
                continue
            if len(article.title) == 0:
                continue
            if bf.is_contains(article.title):
                log.info('文章已经在redis存在,标题={}'.format(article.title))
                continue
            else:
                bf.insert(article.title)
                log.info('新文章，解析文章,标题={}'.format(article.title))
                article.city = city
                if source['comment_count'] is not None:
                    article.comment_count = single_article.xpath(source['comment_count'])[0].strip()
                if source['like_count'] is not None:
                    article.like_count = single_article.xpath(source['like_count'])[0].strip()
                if source['read_num'] is not None:
                    article.read_num = single_article.xpath(source['read_num'])[0].strip()
                if source['title_img'] is not None:
                    try:
                        title_img = single_article.xpath(source['title_img'])[0].strip()
                        article.title_img = title_img
                    except Exception as e:
                        log.info("{}封面图片提取失败".format(article.title))
                if source['post_time'] is not None:
                    try:
                        article.post_time = single_article.xpath(source['post_time'])[0].strip()
                    except:
                        log.info('post_time解析失败')
                        article.post_time = None
                if source['desc'] is not None:
                    try:
                        article.desc = single_article.xpath(source['desc'])[0].strip()
                    except:
                        log.info('无文章简介{}'.format(article.title))

                article_dict = article.to_dict()
                article_dict['detail_url'] = single_article.xpath(source['detail_url'])[0]

                self.channel.queue_declare(queue='usual_article')
                self.channel.basic_publish(exchange='',
                                      routing_key='usual_article',
                                      body=json.dumps(article_dict),
                                      )
                log.info('{}进入usual_article队列'.format(article_dict['source']))

