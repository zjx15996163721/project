import requests
from source_config import Category, City, Region, DevelopmentStage, Block, get_sqlalchemy_session
from lxml import etree
import re

source = 'liepin'
db_session = get_sqlalchemy_session()

def get_city():
    res = requests.get('https://www.liepin.com/citylist/?target=company')
    html = etree.HTML(res.content.decode())
    city_list = html.xpath('//span/a')
    for city in city_list[1:]:
        city_url = city.xpath('./@href')[0]
        city_name = city.xpath('./@title')[0]
        city_id = re.search('/(\d+)-',city_url).group(1)

        city = City()
        city.name = city_name
        city.url = city_url
        city.request_parameter = city_id
        city.source = source
        db_session.add(city)
        db_session.commit()


def get_category():
    cate_res = requests.get('https://www.liepin.com/company/')
    html = etree.HTML(cate_res.content.decode())
    cate_list = html.xpath("//div[@class='sub-industry']/a")
    property_list = html.xpath("//div[@class='kind-name']/a")
    for cate in cate_list:
        cate_url = cate.xpath('./@href')[0]
        cate_name = cate.xpath('./text()')[0]
        cate_id = re.search('-(\d+)', cate_url).group(1)
        for kind in property_list:
            kind_url = kind.xpath('./@href')[0]
            kind_name = kind.xpath('./text()')[0]
            kind_id = re.search('-(\d+)/', kind_url).group(1)

            cate = Category()
            cate.name = cate_name + '-' + kind_name
            cate.source = source
            cate.request_parameter = cate_id + '-' + kind_id

            db_session.add(cate)
            db_session.commit()

if __name__ == '__main__':
    get_city()
    get_category()






