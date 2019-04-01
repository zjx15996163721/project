import yaml
import requests
from article import Article
import json
import datetime
import re
from  article_img.image_replace import ImageReplace
import random
import pika
from lib.log import LogHandler
from lib.proxy_iterator import Proxy

log = LogHandler("fenghuang")
setting = yaml.load(open('config_local.yaml'))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36",
}

proxy = Proxy()


class Consumer:
    def consume_connect(self):
        connect = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbitmq_host'],
                                                                    port=setting['rabbitmq_port'],heartbeat=10))
        self.channel = connect.channel()
        self.channel.queue_declare(queue='fenghuang_article', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                              queue='fenghuang_article',
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

    def callback(self,ch, method, properties, body):
        bod = json.loads(body.decode())
        article = Article(bod['source'])
        article.dict_to_attr(bod)
        url = article.url
        for i in range(10):
            try:
                html = requests.get(url,proxies=next(proxy),timeout=10,headers=headers)
                if html.status_code == 200:
                    con = html.content.decode()
                    break
                elif i == 10 and html.status_code != 200:
                    log.error("请求文章详情页{}失败".format(url))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                log.error(e)
        try:
            article_ready = self.html_parse(con, bod)
        except Exception as e:
            log.error('{}解析失败'.format(url))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        ch.basic_ack(delivery_tag=method.delivery_tag)
        article_ready.insert_db()
        log.info('{}消费一篇文章'.format('凤凰'))

    def html_parse(self,con,bod):
        title = re.search('<div class="title">.*?<h2>(.*?)</h2',con,re.S|re.M).group(1)
        post_time = re.search('<div class="marb-5"><span>(.*?)</span>',con).group(1)
        source_detail = re.search('来源：(.*?)</span',con).group(1)
        readable_article = re.search('<div class="article">.*?</div>',con,re.S|re.M).group(0)

        img_change = ImageReplace()
        readable_article = img_change.image_download(readable_article)

        article = Article(bod['source'])
        article.dict_to_attr(bod)
        article.title = title
        article.post_time = post_time
        article.source_detail = source_detail
        article.body = readable_article
        # article.crawler_time = datetime.datetime.now()
        return article
