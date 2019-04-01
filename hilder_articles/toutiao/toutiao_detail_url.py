"""
selenium 抓取 不用了
"""

from selenium import webdriver
import time
from lib.bloom_filter import BloomFilter
from lib.rabbitmq import Rabbit
from article import Article
import yaml
import json
import re

setting = yaml.load(open('config_local.yaml'))


class Toutiao:
    def __init__(self):
        self.start_url = 'https://www.toutiao.com/ch/news_house/'

        browser = webdriver.ChromeOptions()
        browser.add_argument('--headless')

        self.driver = webdriver.Chrome(chrome_options=browser)

        self.bf = BloomFilter(host=setting['redies_host'],
                              port=setting['redis_port'],
                              key='article_toutiao_test',
                              blockNum=1,
                              db=0, )
        self.rabbit = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'], )

    def start_crawler(self):
        self.driver.get(self.start_url)
        time.sleep(5)
        channel = self.rabbit.get_channel()
        channel.queue_declare(queue='article_test')
        while True:
            self.find_list_info(channel)
            self.driver.refresh()
            time.sleep(20)

    def find_list_info(self, channel):
        article_list = self.driver.find_elements_by_xpath('/html/body/div/div[4]/div[2]/div[2]/div/div/div/ul/li')
        print('len, ', len(article_list))
        for i in article_list:
            if '看到这里' in i.text:
                print('看到这里')
                break
            try:
                wenda = i.find_element_by_xpath('div/div[1]/div/div[2]/div[1]/div/a[2]').text
            except Exception as e:
                continue
            if '悟空问答' in wenda:
                print('悟空问答')
                continue
            article_id = i.get_attribute('group_id')

            # article_id进入布隆过滤器
            if self.bf.is_contains(article_id):
                print('bloom_filter已经存在!')
                continue
            else:
                self.bf.insert(article_id)
                print('bloom_filter不存在，插入article_id!')

                article = Article('今日头条')
                try:
                    organization_author = i.find_element_by_xpath('div/div[1]/div/div[2]/div[1]/div/a[2]').text.replace(
                        '⋅', '')
                    article.organization_author = organization_author.strip()
                except Exception as e:
                    print('没有organization_author')
                title = i.find_element_by_xpath('div/div[1]/div/div[1]/a').text
                article.title = title
                url = i.find_element_by_xpath('div/div[1]/div/div[1]/a').get_attribute('href')
                article.url = url
                # post_time = i.find_element_by_xpath('div/div[1]/div/div[2]/div[1]/span').text
                # article.post_time = post_time

                try:
                    comment_str = i.find_element_by_xpath('div/div[1]/div/div[2]/div[1]/div/a[3]').text
                    comment_count = int(re.search('\d+', comment_str, re.S | re.M).group())
                    article.comment_count = comment_count
                except Exception as e:
                    print('这篇文章没有评论', title)

                try:
                    title_img = i.find_element_by_xpath('div/div[2]/a/img').get_attribute('src')
                    article.title_img = [title_img]
                except Exception as e:
                    print('这篇文章没有list图片:', title)

                print(article.to_dict())
                # 没有在过滤器的文章加入rabbitmq

                channel.basic_publish(exchange='',
                                      routing_key='article_test',
                                      body=json.dumps(article.to_dict()))
                print('已经放入队列')


if __name__ == '__main__':
    t = Toutiao()
    t.start_crawler()
