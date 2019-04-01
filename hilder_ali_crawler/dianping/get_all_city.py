import requests
import re
import json
from dianping.category_orm import City, get_sqlalchemy_session, Region, SecondCategory
from lib.log import LogHandler
import time
db_session = get_sqlalchemy_session()
log = LogHandler(__name__)


class GetAllCity:
    @classmethod
    def get_all_city(cls):
        """
        :return: [city_object, city_object]
        """
        res = requests.get('http://www.dianping.com/ajax/citylist/getAllDomesticCity')
        for values in res.json()['cityMap'].values():
            for city_dict in filter(lambda x: x['parentCityId'] == 0, [city_info for city_info in values]):
                city = City()
                city.name = city_dict['cityName']
                city.city_id = city_dict['cityId']
                city.pingyin_name = city_dict['cityPyName']
                if db_session.query(City).filter_by(city_id=city.city_id).first() is None:
                    print(city.name)
                    db_session.add(city)
                    db_session.commit()
                else:
                    print("已经存在城市")


class GetRegion:
    def __init__(self, city):
        """

        :param city: city_object
        """
        self.city = city
        self.url = 'https://m.dianping.com/{}/ch0/r0'.format(city.pingyin_name)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

    def get_region(self):
        """

        :return: [region_object, region_object, region_object], [category_object,category_object,category_object]
        """
        res = requests.get(self.url, headers=self.headers)
        print(self.url)
        time1 = time.time()
        json_body = re.search('window.PAGE_INITIAL_STATE = (.*?)</script>', res.text, re.S | re.M).group(1)
        body = json.loads(json_body.strip()[:-1])

        # 区域
        try:
            for region_info_dict in filter(
                    lambda region_dict: region_dict['parentId'] == 0 and '热门' not in region_dict['name'],
                    [region_dict for region_dict in body['mapiSearch']['data']['regionNavs']]):
                if db_session.query(Region).filter_by(region_id=region_info_dict['id']).first() is None:
                    region = Region()
                    region.region_id = region_info_dict['id']
                    region.name = region_info_dict['name']
                    region.city_id = self.city.city_id
                    db_session.add(region)
                    db_session.commit()
                    print('添加区域 {}'.format(region.name))
                else:
                    print("已经存在区域")
        except Exception as e:
            log.info('JSON格式错误 {}'.format(body))

        # 二级分类
        try:
            for k in filter(lambda region_dict: region_dict['parentId'] != 0 and '全部' not in region_dict['name'],
                            [region_dict for region_dict in body['mapiSearch']['data']['categoryNavs']]):
                time3 = time.time()
                if db_session.query(SecondCategory).filter_by(second_categoryId=k['id'], cityId=self.city.city_id).first() is None:
                    second_category = SecondCategory()
                    second_category.second_categoryId = k['id']
                    second_category.count = k['count']
                    second_category.name = k['name']
                    second_category.cityId = self.city.city_id
                    second_category.parentId = k['parentId']
                    db_session.add(second_category)
                    db_session.commit()
                    print('添加二级分类 {}'.format(second_category.name))
                else:
                    session = db_session.query(SecondCategory).filter_by(second_categoryId=k['id'], cityId=self.city.city_id).first()
                    session.count = k['count']
                    db_session.commit()
                    print('已经存在二级分类,更新count')
                    time4 = time.time()
                    print('更新一个二级分类的时间 {}'.format(time4 - time3))
        except Exception as e:
            log.info('JSON格式错误 {}'.format(body))
        time2 = time.time()
        print('处理一条URL时间 {}'.format(time2-time1))