import yaml
from lib.rabbitmq import Rabbit
import requests
from readability.readability import Document
from article import Article
import json
import datetime
import re
from html.parser import HTMLParser
import chardet
import random
from  article_img.image_replace import ImageReplace
from lib.log import LogHandler

setting = yaml.load(open('config_local.yaml'))
log = LogHandler("toutiao_consumer")
html_parser = HTMLParser()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Cache-Control': "no-cache",
    'Postman-Token': "e9b36b12-5a36-a9a3-8cb9-468a08e028a7"
}


proxies = [{"http": "http://192.168.0.96:4234"},
           {"http": "http://192.168.0.93:4234"},
           {"http": "http://192.168.0.90:4234"},
           {"http": "http://192.168.0.94:4234"},
           {"http": "http://192.168.0.98:4234"},
           {"http": "http://192.168.0.99:4234"},
           {"http": "http://192.168.0.100:4234"},
           {"http": "http://192.168.0.101:4234"},
           {"http": "http://192.168.0.102:4234"},
           {"http": "http://192.168.0.103:4234"}, ]


class Toutiao_Consumer:
    def __init__(self):
        self.rabbit = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'], )

    @staticmethod
    def parse_html(res):
        # res = requests.get(url=url, headers=headers)

        # 切割url()
        # article_id = re.search('\d+', url).group()
        if 'articleInfo' in res.text:
            # 今日头条的url
            readable_title = Document(res.content).short_title()
            readable_article_ = re.search("articleInfo.*?content.*?'(.*?)'", res.content.decode(), re.S | re.M).group(1)
            readable_article = html_parser.unescape(readable_article_)
            source_detail = '今日头条'
            img_change = ImageReplace()
            readable_article = img_change.image_download(readable_article)    #对今日头条来源的文章内容进行图片连接替换

        else:
            # 其他来源的文章
            html_byte = re.sub(b'<script.*script>', b'', res.content, )
            encode_dict = chardet.detect(html_byte)
            encode_type = encode_dict['encoding']
            readable_title = Document(html_byte.decode(encode_type)).short_title()
            readable_article = Document(html_byte.decode(encode_type)).summary()
            source_detail = 'other'
        return readable_title, readable_article,source_detail

    @staticmethod
    def get_post_time(res):
        if 'articleInfo' in res.text:
            # 今日头条的url
            time = re.search("time: '(.*?)'", res.content.decode(), re.S | re.M).group(1)
            return time
        else:
            return None

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        article = Article(body['source'])
        article.dict_to_attr(body)
        url = article.url

        while True:
            try:
                res = requests.get(url=url, headers=headers, proxies=proxies[random.randint(0, 9)], timeout=10)
                res.encoding = 'utf-8'
                if '<html><head></head><body></body></html>' not in  res.text:
                    break
            except Exception as e:
                log.error('网络请求错误{}'.format(e))

        readable_title, readable_article,source_detail = self.parse_html(res)
        article.post_time = self.get_post_time(res)
        article.body = readable_article
        article.source_detail  = source_detail
        article.crawler_time = datetime.datetime.now()
        if '<body id="readabilityBody"/>' in article.body:
            log.info("文章为空")
        else:
            article.insert_db()
            log.info('{}一篇文张入库成功'.format('今日头条'))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_connect(self):
        connect = self.rabbit.get_connection()
        self.channel = connect.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                              queue='toutiao',
                              no_ack=False)

    def start_consume(self):
        disconnected = True
        while disconnected:
            try:
                disconnected = False
                self.channel.start_consuming()
            except Exception as e:
                disconnected = True
                self.consume_connect()


if __name__ == '__main__':
    toutiao = Toutiao_Consumer()
    toutiao.start_consume()