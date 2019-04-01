import requests
from lxml import etree
from pymongo import MongoClient
from lib.rabbitmq import Rabbit
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
import yaml
import json
import datetime
import re
import time


setting = yaml.load(open('config_local.yaml'))
log = LogHandler('article_consumer')
m = MongoClient(setting['mongo_config']['config_host'], setting['mongo_config']['port'])
m.admin.authenticate(setting['mongo_config']['user_name'],setting['mongo_config']['password'] )
collection = m[setting['mongo_config']['config_db']][setting['mongo_config']['coll_detail']]
clean_coll = m[setting['mongo_config']['config_db']][setting['mongo_config']['clean']]
rabbit = Rabbit(setting['rabbitmq_host'],setting['rabbitmq_port'])
connection = rabbit.connection


class CrawlerDetail:

    def __init__(self):
        self.proxy = Proxies()

    def start_consume(self):
        channel = connection.channel()
        channel.queue_declare(queue='usual_article')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.consume_article_detail_url,
                                   queue='usual_article',
                                   no_ack=False)
        channel.start_consuming()

    def clean(self,message):
        """
        作者,发布时间,详细来源字段清洗
        :param message:
        :return:
        """
        clean = clean_coll.find_one({'source': message['source']})
        if clean['post_time'] is not None:
            try:
                post_time = re.search(clean['post_time'],message['post_time'],re.S|re.M).group(1)
                message['post_time'] = post_time
            except:
                log.info("post_time清洗失败{}".format(message['post_time']))
                message['post_time'] = None
        if clean['author'] is not None:
            try:
                author = re.search(clean['author'],message['author']).group(1)
                message['author'] = author
            except:
                log.info("author清洗失败{}".format(message['author']))
                message['author'] = None

        if clean['source_detail'] is not None:
            try:
                source_detail = re.search(clean['source_detail'],message['source_detail'],re.S|re.M).group(1)
                message['source_detail'] = source_detail
            except:
                log.info("source_detail清洗失败{}".format(message['source_detail']))
                message['source_detail'] = None

        return message


    def consume_article_detail_url(self,ch, method, properties, body):
        """
        文章详情页解析
        :param ch:
        :param method:
        :param properties:
        :param body: json格式字符串
        :return:
        """
        message = json.loads(body.decode())
        for i in range(10):
            try:
                html = requests.get(message['detail_url'],timeout=10,proxies=next(self.proxy))
                connection.process_data_events()
                if html.status_code == 200:
                    break
            except Exception as e:
                connection.process_data_events()
                if i == 10:
                    log.error("请求文章详情页{}失败".format(message['detail_url']))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            con = html.content.decode()
        except:
            try:
                con = html.content.decode('gbk')
            except:
                log.error('{}utf-8,gbk编码解析失败'.format(message['detail_url']))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        page = etree.HTML(con)

        # 获取详情页的解析方式
        detail_config_dict = collection.find_one({'source': message['source']})

        if detail_config_dict['body'] is not None:
            try:
                for pattern in detail_config_dict['body']:
                    if page.xpath(pattern):
                        article_body = page.xpath(pattern)[0]
                        message['body'] = etree.tounicode(article_body)
                        break
            except:
                log.error('xpath语句未能解析body')
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        if detail_config_dict['comment_count'] is not None:
            message['comment_count'] = page.xpath(detail_config_dict['comment_count'])[0]
        if detail_config_dict['like_count'] is not None:
            message['like_count'] = page.xpath(detail_config_dict['like_count'])[0]
        if detail_config_dict['read_num'] is not None:
            message['read_num'] = page.xpath(detail_config_dict['read_num'])[0]
        if detail_config_dict['author'] is not None:
            try:
                message['author'] = page.xpath(detail_config_dict['author'])[0]
            except:
                log.info("没有提取到{}作者字段".format(message['detail_url']))
        if detail_config_dict['post_time'] is not None:
            try:
                message['post_time'] = page.xpath(detail_config_dict['post_time'])[0]
            except:
                log.info("没有提取到{}文章发表时间".format(message['detail_url']))
        if detail_config_dict['tag'] is not None:
            message['tag'] = page.xpath(detail_config_dict['tag'])[0]
        if detail_config_dict['source_detail'] is not None:
            try:
                message['source_detail'] = page.xpath(detail_config_dict['source_detail'])[0]
            except:
                log.info("没有提取到{}文章详细来源".format(message['detail_url']))

        self.clean(message)

        # 放入消息队列做正文替换清洗
        produce_channel = connection.channel()
        produce_channel.queue_declare('article_body')
        article_text = json.dumps(message)
        produce_channel.basic_publish(exchange='',
                              routing_key='article_body',
                              body=article_text)
        log.info('{}已经放入清洗队列'.format(message['title']))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        produce_channel.close()