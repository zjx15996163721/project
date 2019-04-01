import requests
import json
from lib.bloom_filter import BloomFilter
from lib.rabbitmq import Rabbit
from lib.log import LogHandler
import re
import yaml
from article import Article
from toutiao.comment_temp import Comment_url
import datetime
import time
import random
from article_img.qiniu_fetch import qiniufetch

setting = yaml.load(open('config_local.yaml'))
log = LogHandler('toutiao_queue')

class Toutiao:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"

            }
        self.start_url = "http://is.snssdk.com/api/news/feed/v46/?category=news_house"
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
        self.rabbit = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'])

    def start_crawler(self):

        channel = self.rabbit.get_channel()
        channel.queue_declare(queue='toutiao')
        while True:
            try:
                self.url_list_crawler(channel)
                time.sleep(60)
            except:
                continue

    def url_list_crawler(self, channel):
        while True:
            proxy = self.proxies[random.randint(0,9)]
            try:
                response = requests.get(self.start_url, headers=self.headers, proxies=proxy)
                url_dict = json.loads(response.text)
                url_list = url_dict["data"]
                break
            except:
                continue
        for url_content in url_list:
            con = url_content["content"]
            try:
                url = re.search('display_url":"(.*?)"', con).group(1)
            except:
                continue
            if re.search('wukong', url):
                continue
            else:
                if self.bf.is_contains(url):  # 过滤详情页url
                    log.info('bloom_filter已经存在{}'.format(url))
                    continue
                else:
                    self.bf.insert(url)
                    log.info('bloom_filter不存在，插入新的url:{}'.format(url))
                    article = Article('今日头条')
                    comment_code = Comment_url()
                    try:
                        organization_author = re.search('\\"source\\":\\"(.*?)\\"', con).group(1)
                        article.organization_author = organization_author
                    except Exception as e:
                        log.info('没有organization_author')
                    title = re.findall('"title":"(.*?)"', con)[1]
                    article.title = title
                    article.url = url
                    article.article_id = re.search('group/(\d+)', url).group(1)
                    comment_code.group_id = article.article_id
                    comment_code.crawler_time = datetime.datetime.utcnow()
                    try:
                        comment_count = re.search('\\"comment_count\\":(\d+)', con).group(1)
                        article.comment_count = comment_count
                        comment_code.comment_count = comment_count
                    except Exception as e:
                        log.info('{}这篇文章没有评论'.format(title))
                    try:
                        title_img = re.search('middle_image.*?"url":"(.*?.webp)', con).group(1)
                        new_title_img = qiniufetch(title_img,title_img)
                        article.title_img = new_title_img
                    except Exception as e:
                        log.info('{}这篇文章没有list图片:'.format(title))

                    channel.basic_publish(
                        exchange='',
                        routing_key='toutiao',
                        body=json.dumps(article.to_dict())
                    )
                    log.info('已经放入队列')


if __name__ == '__main__':
    toutiao = Toutiao()
    toutiao.start_crawler()
