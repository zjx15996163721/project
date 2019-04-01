from .qiniu_fetch import qiniufetch
import re
import yaml
from lib.log import LogHandler
from lib.rabbitmq import Rabbit
import json
from article import Article
import datetime
import time

setting = yaml.load(open('config_local.yaml'))
log = LogHandler("img_replace")

rabbit = Rabbit(setting['rabbitmq_host'], setting['rabbitmq_port'])
connection = rabbit.connection


class ReplaceException(Exception):
    def __str__(self):
        return '文章图像替换错误'


class CleanUp:
    def start_consume(self):
        channel = connection.channel()
        channel.queue_declare(queue='article_body')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.image_download,
                              queue='article_body',
                              no_ack=False)

        channel.start_consuming()

    def image_check(self, image_url_list, message, method, ch, article, pattern):
        """
        文章图片替换
        :param image_url_list: 文章body中所有图片
        :param message:
        :param method:
        :param ch:
        :param article: 文章body
        :param pattern: 图片替换规则
        :return:
        """
        if message['title_img'] is not None:
            img = message['title_img']
            title_img = qiniufetch(img, img)
            connection.process_data_events()
            if title_img is False:
                log.info("{}封面图片提取失败".format(article.title))
            else:
                message['title_img'] = title_img
                log.info("已上传{}封面图片".format(message['title']))

        if len(image_url_list) == 0:
            self.news_insert(message)
            detail_url = message.pop('detail_url')
            message['url'] = detail_url
            log.info('{}无图片可更换！'.format(detail_url))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            detail_url = message.pop('detail_url')
            message['url'] = detail_url
            try:
                new_body = re.sub(pattern, self.replace, article)
            except ReplaceException as e:
                log.error('图片替换失败{}'.format(e))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            message['body'] = new_body
            self.news_insert(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log.info('{}已入库'.format(detail_url))

    @staticmethod
    def news_insert(message):
        """
        数据入库
        :param message:
        :return:
        """
        news = Article(message['source'])
        news.dict_to_attr(message)
        news.insert_db()

    def image_download(self, ch, method, properties, body):
        message = json.loads(body.decode())
        article = message['body']
        message = self.post_time_standard(message)
        try:
            if re.findall('data-src="(.*?)"', article):
                pattern = 'data-src="(.*?)"'
                image_url_list = re.findall('data-src="(.*?)"', article)
                self.image_check(image_url_list, message, method, ch, article, pattern)
            else:
                image_url_list = re.findall('src="(.*?)"', article)
                pattern = 'src="(.*?)"'
                self.image_check(image_url_list, message, method, ch, article, pattern)
        except Exception as e:
            log.error("{}文章文本提取有误{}".format(message['url'], e))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    def replace(match_object):
        image_url = match_object.group(1)
        connection.process_data_events()
        image_new_url = qiniufetch(image_url, image_url)
        connection.process_data_events()
        if image_new_url is False:
            raise ReplaceException
        else:
            return 'src="' + image_new_url + '"'

    def post_time_standard(self,message):
        """
        post_time标准化
        :param message:
        :return:
        """
        if message['post_time'] is None:
            return message
        elif '年' in message['post_time']:
            try:
                post_time = re.search('\d+年\d+月\d+日', message['post_time'].strip()).group(0)
                t = time.strptime(post_time,"%Y年%m月%d日")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                message['s_post_time'] = datetime.datetime(y, m, d)
            except:
                log.error("发表时间正则匹配失败{}".format(message['post_time']))
                message['s_post_time'] = None
        else:
            try:
                post_time = re.search('\d+-\d+-\d+',message['post_time'].strip()).group(0)
                t = time.strptime(post_time, "%Y-%m-%d")
                y = t.tm_year
                m = t.tm_mon
                d = t.tm_mday
                message['s_post_time'] = datetime.datetime(y, m, d)
            except:
                log.error("发表时间正则匹配失败{}".format(message['post_time']))
                message['s_post_time'] = None
        return message