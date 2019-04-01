import yaml
import pika
import requests
from article import Article
import json
from lxml import etree
import datetime
import re
from  article_img.image_replace import ImageReplace
import random
from lib.log import LogHandler
from lib.proxy_iterator import Proxy

log = LogHandler("wangyi")
setting = yaml.load(open('config_local.yaml'))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36",
}
proxy = Proxy()

class WangyiConsumer:

    def consume_connect(self):
        connect = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbitmq_host'],
                                                                    port=setting['rabbitmq_port'],heartbeat=10))
        self.channel = connect.channel()
        self.channel.queue_declare(queue='wangyi_article', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                              queue='wangyi_article',
                              no_ack=False)
    def start_consume(self):
        disconnected = True
        while disconnected:
            try:
                disconnected = False
                self.channel.start_consuming()
            except Exception as e:
                log.error(e)
                disconnected = True
                self.consume_connect()

    def callback(self, ch, method, properties, body):
        bod = json.loads(body.decode())
        article = Article(bod['source'])
        article.dict_to_attr(bod)
        url = article.url

        for i in range(10):
            try:
                res = requests.get(url, proxies=next(proxy), timeout=10)  # 代理
                res.encoding = 'gbk'
                con = res.text
                if res.status_code == 200:
                    break
                elif i == 10 and res.status_code != 200:
                    log.error("{}列表页访问失败".format(url))
            except Exception as e:
                log.error('网络请求错误')

        try:
            article_ready = self.html_parse(con, bod)
        except Exception as e:
            log.error(e)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        ch.basic_ack(delivery_tag=method.delivery_tag)
        article_ready.insert_db()
        log.info('{}消费一篇文章'.format('网易新闻'))

    def html_parse(self, con, bod):
        html = etree.HTML(con)
        title = re.search('<h1>(.*?)</h1>',con).group(1)
        post_time = re.search('post_time_source">(.*?)　来源',con,re.S|re.M).group(1)
        source_detail = re.search('来源:.*?>(.*?)</',con).group(1)
        try:
            author = re.search('作者：(.*?)</',con).group(1)
        except:
            author = None
        news_html = html.xpath("//div[@class='post_text']")[0]
        readable_article = etree.tounicode(news_html)

        img_change = ImageReplace()
        readable_article = img_change.image_download(readable_article)
        article = Article(bod['source'])
        article.dict_to_attr(bod)
        article.title = title
        article.post_time = post_time
        article.source_detail = source_detail
        article.body = readable_article
        article.author = author
        article.crawler_time = datetime.datetime.now()
        return article
