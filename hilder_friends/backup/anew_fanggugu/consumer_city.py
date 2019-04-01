import requests
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from urllib import parse
from lib.log import LogHandler
from backup.anew_fanggugu.user_names import username_list
from progressbar import *

log = LogHandler(__name__)

r = Rabbit('127.0.0.1', 5673)
channel = r.get_channel()
channel.queue_declare(queue='fgg_user_city')

m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
# m = Mongo('127.0.0.1', 27018)
coll_comm = m.connect['fgg']['comm']
coll_build = m.connect['fgg']['build']
coll_house = m.connect['fgg']['house']


class ConsumerCity(object):
    """
        获取所有的城市的小区,楼栋,房号,面积
    """

    def __init__(self):
        self.p = ProgressBar()
        self.headers = {'Authorization': ""}
        self.s = requests.session()
        self.currentCity = ''
        self.currentCityPy = ''
        self.username = ''
        self.password = ''

    # 登陆
    def login(self):
        url_login = "http://fggfinance.yunfangdata.com/WeChat/webservice/doLogin"
        data = {'openid': 'ohWOiuP_gteNNJemGpvDG1axnbBc', 'password': self.password, 'userName': self.username}
        headers_login = {
            'Content-Length': "0",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/66.0.3359.117 Safari/537.36",
            'Cache-Control': "no-cache",
        }
        response = requests.post(url_login, data=data, headers=headers_login)
        access_token = response.json()['data']['access_token']['access_token']
        token_type = response.json()['data']['access_token']['token_type']
        authorization = token_type + ' ' + access_token
        self.headers['Authorization'] = authorization
        log.info('登陆成功')
        self.get_city_info()

    # 获取当前账号的城市
    def get_city_info(self):
        try:
            city_url = 'http://fggfinance.yunfangdata.com/WeChat/xiaoQuChaXun/getCurrentCity'
            response = requests.get(city_url, headers=self.headers)
            if response.json()['success']:
                data = response.json()['data']
                self.currentCity = data['currentCity']
                self.currentCityPy = data['currentCityPy']
                log.info('检测当前城市为,city="{}"'.format(self.currentCity))
            else:
                log.error('检测城市失败,重新检测')
                self.get_city_info()
        except Exception as e:
            log.error('检测城市失败,重新检测')
            self.get_city_info()

    # 扫描1-50000的id
    def get_all_info(self):
        self.login()
        for comm_id in range(0, 50000):
            self.get_comm_info(str(comm_id))

    # 请求comm详情信息
    def get_comm_info(self, comm_id):
        try:
            city_parse = parse.quote_plus(self.currentCity)
            url = "http://fggfinance.yunfangdata.com/WeChat/xiaoQuChaXun/getXiaoQuXinXi?cityName=" \
                  + city_parse + "&msgType=%E6%99%AE%E9%80%9A%E6%9F%A5%E8%AF%A2&residentialAreaId=" \
                  + str(comm_id)
            response = requests.get(url, headers=self.headers)
            if response.json()['success']:
                if response.json()['data']['baseInfoMap']:
                    data = response.json()['data']
                    data['comm_id'] = str(comm_id)
                    data['city'] = self.currentCity
                    log.info('获取小区信息成功,data="{}"'.format(data))
                    coll_comm.update_one({'comm_id': comm_id}, {'$set': data}, upsert=True)
                    # channel.basic_publish(exchange='',
                    #                       routing_key='fgg_comm_id',
                    #                       body=str(comm_id))
                    # self.get_build_info(comm_id)
            else:
                self.login()
                self.get_comm_info(comm_id)
        except Exception as e:
            self.get_comm_info(comm_id)

    # 请求build信息
    def get_build_info(self, comm_id):
        try:
            url = "http://fggfinance.yunfangdata.com/WeChat/JinRongGuZhi/getFangWuZuoLuo?cityNamePy=" \
                  + self.currentCityPy + "&id=" + str(comm_id) + "&type=xiaoqu"
            response = requests.get(url, headers=self.headers)
            if response.json()['success']:
                if response.json()['data']:
                    for build in response.json()['data']:
                        build['comm_id'] = str(comm_id)
                        build['city'] = self.currentCity
                        build['id'] = str(build['id'])
                        build['build_id'] = build.pop('id')
                        build_id = build['build_id']
                        build_type = build['type']
                        log.info('获取楼栋信息成功,data="{}"'.format(build))
                        coll_build.insert_one(build)
                        if build_type == 'danyuan':
                            self.get_house_info(build_id, build_type)
                        elif build_type == 'louzhuang':
                            self.get_unit_info(build_id, build_type)
                        else:
                            print('*' * 100)
                            print('build_type:', build_type)
            else:
                self.login()
                self.get_build_info(comm_id)
        except Exception as e:
            self.login()
            self.get_build_info(comm_id)

    # 请求unit信息
    def get_unit_info(self, build_id, build_type):
        try:
            url = "http://fggfinance.yunfangdata.com/WeChat/JinRongGuZhi/getFangWuZuoLuo?cityNamePy=" \
                  + self.currentCityPy + "&id=" + build_id + "&type=" + build_type
            response = self.s.get(url, headers=self.headers)
            if response.json()['success']:
                if response.json()['data']:
                    for unit in response.json()['data']:
                        unit_id = str(unit['id'])
                        unit_name = unit['name']
                        unit_type = unit['type']
                        unit_info = {'unit_id': unit_id, 'unit_name': unit_name, 'unit_type': unit_type,
                                     'build_id': build_id}
                        self.get_house_info(unit_id, unit_type, unit_info)
            else:
                self.login()
                self.get_unit_info(build_id, build_type)
        except Exception as e:
            self.get_unit_info(build_id, build_type)

    # 请求house信息
    def get_house_info(self, build_id, build_type, unit_info=None):
        try:
            url = "http://fggfinance.yunfangdata.com/WeChat/JinRongGuZhi/getFangWuZuoLuo?cityNamePy=" \
                  + self.currentCityPy + "&id=" + build_id + "&type=" + build_type
            response = self.s.get(url, headers=self.headers)
            if response.json()['success']:
                if response.json()['data']:
                    for house in response.json()['data']:
                        # 判断是否有单元,如果有合并单元信息,否则加入楼栋对应关系
                        if unit_info:
                            house.update(unit_info)
                        else:
                            house['build_id'] = str(build_id)
                        house['city'] = self.currentCity
                        house_id = str(house['id'])
                        self.get_area_info(house_id, house)
            else:
                self.login()
                self.get_house_info(build_id, build_type)
        except Exception as e:
            self.get_house_info(build_id, build_type)

    # 请求area信息
    def get_area_info(self, house_id, house):
        try:
            url = "http://fggfinance.yunfangdata.com/WeChat/JinRongGuZhi/getHouseInfo?cityNamePy=" \
                  + self.currentCityPy + "&houseId=" + house_id
            response = self.s.get(url, headers=self.headers)
            if response.json()['success']:
                if response.json()['data']:
                    area = response.json()['data']
                    house.update(area)
                    log.info('获取房号信息成功,data="{}"'.format(house))
                    house['id'] = str(house['id'])
                    house['house_id'] = house.pop('id')
                    coll_house.insert_one(house)

            else:
                self.login()
                self.get_area_info(house_id, house)
        except Exception as e:
            self.get_area_info(house_id, house)

    # 开始方法
    def start_crawler(self):
        for i in username_list:
            self.username = i['username']
            self.password = i['password']
            self.get_all_info()


if __name__ == '__main__':
    c = ConsumerCity()
    c.start_crawler()
