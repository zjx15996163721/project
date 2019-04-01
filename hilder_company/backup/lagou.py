import requests
from source_config import Category, City, Region, DevelopmentStage, Block, get_sqlalchemy_session
from lxml import etree
import re

db_session = get_sqlalchemy_session()


class Lagou:
    def __init__(self):
        self.source = 'lagou'
        self.url = 'https://www.lagou.com/'
        self.city_url = 'https://www.lagou.com/jobs/allCity.html?'

    def get_all_city(self):
        """
        run once
        :return:
        """
        r = requests.get(self.city_url)
        html = etree.HTML(r.text)
        city_info = html.xpath('//*[@id="main_container"]/div/div/table[2]/tr/td/ul/li/a')
        for i in city_info:
            city_name = i.text
            city_url = i.attrib['href']
            city_pinyin = re.search('com/(.*?)/', city_url).group(1)

            city = City()
            city.name = city_name
            city.url = city_url
            city.request_parameter = city_pinyin
            city.source = self.source

            db_session.add(city)
            db_session.commit()

    def get_all_category(self):
        pass

    def get_page(self):
        pass
