from dianping.category_orm import SecondCategory, Region, get_sqlalchemy_session
import requests
from lib.log import LogHandler
import pika
from lib.proxy_iterator import Proxies
import yaml

setting = yaml.load(open('config_dianping.yaml'))

log = LogHandler(__name__)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()

REQUEST_LIMIT = 5000
db_session = get_sqlalchemy_session()
p = Proxies()


class Controller:
    def __init__(self, proxies):
        self.url = 'https://mapi.dianping.com/searchshop.json?'
        self.headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
                'Referer': 'https://m.dianping.com/'
            }
        self.proxies = proxies

    def crawler_by_city(self, city):
        """
        :param city: city ORM
        :return:
        """
        second_category_list = db_session.query(SecondCategory).filter_by(cityId=city.city_id).all()
        for second_category in second_category_list:
            if int(second_category.count) <= REQUEST_LIMIT:
                # 小于5000的抓取
                self.crawler_all_shop(second_category)
            else:
                # 大于5000的抓取 通过区域
                self.crawler_shop_by_region(second_category)

    def crawler_all_shop(self, second_category):
        """
        小于5000的抓取
        :param second_category: second_category ORM
        :return:
        """
        print('小于5000条')
        for i in range(int(second_category.count / 50) + 1):
            params = 'start={}&cityid={}&categoryid={}&limit={}'.format(i * 50, second_category.cityId, second_category.second_categoryId, '50')
            self.category_produce(url=self.url + params)
            print('放队列 {}'.format(self.url + params))

    def crawler_shop_by_region(self, second_category):
        """
        大于5000，通过区域抓取 ,每次最多抓5000条
        :return:
        """
        print('大于5000条')
        for region in db_session.query(Region).filter_by(city_id=second_category.cityId):
            payload = 'start={}&regionid={}&cityid={}&categoryid={}&limit={}'.format(0, region.region_id, second_category.cityId, second_category.second_categoryId, '50')
            print('city={}, region={}'.format(second_category.cityId, region.region_id))
            try:
                r = requests.get(self.url + payload, headers=self.headers, proxies=self.proxies)
                region_count = r.json()['recordCount']
                if region_count > REQUEST_LIMIT:
                    region_count = 5000
                    print('count = {}'.format(int(region_count / 50) + 1))
                for i in range(int(region_count / 50) + 1):
                    # &sortid=8 低价优先 &sortid=9 高价优先 正反排序
                    params_low = 'start={}&regionid={}&cityid={}&categoryid={}&limit={}&sortid=8'.format(i * 50, region.region_id, second_category.cityId, second_category.second_categoryId, '50')
                    params_high = 'start={}&regionid={}&cityid={}&categoryid={}&limit={}&sortid=9'.format(i * 50, region.region_id, second_category.cityId, second_category.second_categoryId, '50')
                    params_list = [params_low, params_high]
                    for params in params_list:
                        self.category_produce(url=self.url + params)
                        print('放队列 {}'.format(self.url + params))
            except Exception as e:
                print(e)
                log.info('请求失败={}'.format(self.url + payload))
                print('切换代理')
                self.proxies = next(p)

    @staticmethod
    def category_produce(url):
        channel.queue_declare(queue='category_list_url')
        channel.basic_publish(exchange='',
                              routing_key='category_list_url',
                              body=url)
