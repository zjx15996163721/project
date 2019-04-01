"""
猎聘生产者，url是分页url ,将url存储到liepin_page队列中，方便消费者进行异步消费
"""
import re
import requests
from lib.log import LogHandler
from source_config import Category, City, get_sqlalchemy_session
import pika
import yaml
import json

log = LogHandler('liepin_producer_list')
db_session = get_sqlalchemy_session()
setting = yaml.load(open('config.yaml'))
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=setting['rabbitmq']['host'],
    port=setting['rabbitmq']['port'],
    heartbeat=0
))
channel = connection.channel()


class LiepinProduceList:
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.proxies = proxies

    def start_crawler(self):
        city_list = db_session.query(City).filter_by(source='liepin')
        cate_list = db_session.query(Category).filter_by(source='liepin')
        for city in city_list:
            city_id = city.request_parameter
            city_name = city.name
            print(city_name, city_id)
            for cate in cate_list:
                cate_id = cate.request_parameter
                index_url = 'https://www.liepin.com/company/' + city_id + '-' + cate_id
                print(index_url)
                self.fetch_index(index_url)
        # connection.close()

    def fetch_index(self, url):
        try:
            res = requests.get(url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('出错了，错误原因{},需要切换ip'.format(e))
            requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
            return
        self.index_parse(url, res)

    def index_parse(self, url, resp):
        page = re.search('共(\d+)页', resp.content.decode())
        print('总页数为{}'.format(page))
        if page is None:
            log.info('没有分页')
            self.fetch_page(url, 1)
        else:
            print(page)
            pagecount = page.group(1)
            print(pagecount)
            self.fetch_page(url, pagecount)

    def fetch_page(self, url, page):
        '''
        #注意：url上面页数比真正的页数少1
        :param url:应该是第一页的url
        :param page:总页数
        :return:
        '''
        channel.queue_declare(queue='liepin_producer_list')
        for i in range(int(page)):
            if i == 0:
                page_url = url
            else:
                page_url = url + '/pn' + str(i)
            print('将分页page_url放入到liepin_producer_list队列中{}'.format(page_url))
            channel.basic_publish(
                exchange='',
                routing_key='liepin_producer_list',
                body=json.dumps(page_url)
            )
