"""
二手成交数据字段

入43基础数据库
43数据字段类型严格按照下面字段对应
这是一个父类,一些通用的属性和方法可以通过子类继承
"""
from lib.log import LogHandler
from pymongo import MongoClient
import yaml
import time
from datetime import datetime
from lib.standardization import StandardCity

log = LogHandler(__name__)
setting = yaml.load(open('config_local.yaml'))

m = MongoClient(host=setting['mongo']['host'],
                port=setting['mongo']['port'],
                username=setting['mongo']['user_name'],
                password=setting['mongo']['password'])
# 43数据库 fangjia dealprice 表
db = m[setting['mongo']['db_name']]
crawler_collection = db[setting['mongo']['coll_comm']]


class Base(object):

    def __init__(self, source, trade_date=None, city=None, region=None, district_name=None,
                 avg_price=None, house_num=None, unit_num=None, total_price=None,
                 room_num=None, area=None, direction=None, fitment=None, height=None,
                 floor=None, room=None, hall=None, toilet=None, url=None, m_date=None):
        self.city = city                                            # 城市
        self.region = region                                        # 区域
        self.district_name = district_name                          # 小区名
        self.avg_price = avg_price                                  # 均价 Int 元/平方米
        self.total_price = total_price                              # 总价 Int 单位元
        self.house_num = house_num                                  # 楼栋号 string
        self.unit_num = unit_num                                    # 单元号 string
        self.room_num = room_num                                    # 室号 string
        self.area = area                                            # 面积 float
        self.direction = direction                                  # 朝向
        self.fitment = fitment                                      # 装修
        self.source = source                                        # 来源网站
        self.room = room                                            # 室数 Int
        self.hall = hall                                            # 厅数 Int
        self.toilet = toilet                                        # 卫数 Int
        self.height = height                                        # 总楼层 Int
        self.floor = floor                                          # 所在楼层 Int
        self.trade_date = trade_date                                # 交易时间
        self.m_date = m_date                                        # 更新时间
        self.create_date = datetime.utcnow()                        # 创建时间
        self.packing_space = False                                  # 添加标记，默认为False,如果有地下或者车位的改为True
        self.url = url  # 链接

    @staticmethod
    def compare(comm_keys):
        """
        防止程序员瞎写错误字段
        :param comm_keys: 字典
        :return:
        """
        c = Base(source=None)
        for i in comm_keys:
            if i not in vars(c).keys():
                raise KeyError

    @staticmethod
    def serialization_info(info):
        """
        对象转字典
        :param info:
        :return: data:字典
        """
        data = {}
        for key, value in vars(info).items():
            data[key] = value
        return data

    def insert_db(self):
        data = self.serialization_info(self)
        self.compare(data)
        try:
            self.check_data_type(data)
        except Exception as e:
            log.error(e)
            return
        try:
            self.check_data_validity(data)
        except Exception as e:
            log.error(e)
            return
        standard = StandardCity()
        city_success, data['city'] = standard.standard_city(data['city'])
        region_success, data['region'] = standard.standard_region(data['city'], data['region'])
        if data['room_num'] is not None:
            if '地下' in data['room_num'] or '车位' in data['room_num']:
                data['packing_space'] = True
        if city_success is False or region_success is False:
            log.error('城市区域数据格式化失败data={}'.format(data))
        elif not crawler_collection.find_one({'city': data['city'],
                                              'region': data['region'],
                                              'district_name': data['district_name'],
                                              'source': data['source'],
                                              'avg_price': data['avg_price'],
                                              'trade_date': data['trade_date'],
                                              'area': data['area']}):
            crawler_collection.insert_one(data)
            log.info('一条数据入43库={}'.format(data))
            return True
        else:
            log.info('已经存在数据={}'.format(data))
            return True

    @staticmethod
    def check_data_validity(data):
        """
        验证成交数据的合法性
        :param data: 字典
        :return:
        """
        # 小区名字段
        if data['district_name'] is None:
            raise Exception('{} district_name is None!'.format(data['source']))
        # 房屋面积范围
        if data['area'] is None or data['area'] < 10 or data['area'] > 1000:
            raise Exception('{} {} {} Area is illegal:{}'.format(data['source'],
                                                                 data['city'],
                                                                 data['district_name'],
                                                                 data['area']))
        # 总价范围
        if data['total_price'] is None or data['total_price'] <= 10000:
            raise Exception('{} {} {} TotalPrice is illegal:{}'.format(data['source'],
                                                                       data['city'],
                                                                       data['district_name'],
                                                                       data['total_price']))
        # 均价范围
        if data['avg_price'] is None or data['avg_price'] < 1000 or data['avg_price'] > 50 * 10000:
            raise Exception('{} {} {} AvgPrice is illegal:{}'.format(data['source'],
                                                                     data['city'],
                                                                     data['district_name'],
                                                                     data['avg_price']))
        # 成交日期范围
        if data['trade_date'] is None or data['trade_date'] < datetime(2003, 1, 1) or data['trade_date'] > datetime.now():
            raise Exception('{} {} {} trade_date is illegal:{}'.format(data['source'],
                                                                       data['city'],
                                                                       data['district_name'],
                                                                       data['trade_date']))

    @staticmethod
    def check_data_type(data):
        """
        self.room = room                    # 室数 Int
        self.hall = hall                    # 厅数 Int
        self.toilet = toilet                # 卫数 Int
        self.height = height                # 总楼层 Int
        self.floor = floor                  # 所在楼层 Int
        self.avg_price = avg_price          # 均价 Int 元/平方米
        self.total_price = total_price      # 总价 Int 单位元
        self.area = area                    # 面积 float
        :param data:
        :return:
        """
        if type(data['room']) == int or data['room'] is None:
            pass
        else:
            raise Exception('room类型错误')

        if type(data['hall']) == int or data['hall'] is None:
            pass
        else:
            raise Exception('hall类型错误')

        if type(data['toilet']) == int or data['toilet'] is None:
            pass
        else:
            raise Exception('toilet类型错误')

        if type(data['height']) == int or data['height'] is None:
            pass
        else:
            raise Exception('height类型错误')

        if type(data['floor']) == int or data['floor'] is None:
            pass
        else:
            raise Exception('floor类型错误')

        if type(data['avg_price']) == int:
            pass
        else:
            raise Exception('avg_price类型错误')

        if type(data['total_price']) == int:
            pass
        else:
            raise Exception('total_price类型错误')

        if type(data['area']) == float:
            pass
        else:
            raise Exception('area类型错误')

    '''UTC时间转本地时间（+8:00）'''
    @staticmethod
    def utc2local(utc_st):
        now_stamp = time.time()
        local_time = datetime.fromtimestamp(now_stamp)
        utc_time = datetime.utcfromtimestamp(now_stamp)
        offset = local_time - utc_time
        local_st = utc_st + offset
        return local_st

    '''本地时间转UTC时间（-8:00）'''
    @staticmethod
    def local2utc(local_st):
        time_struct = time.mktime(local_st.timetuple())
        utc_st = datetime.utcfromtimestamp(time_struct)
        return utc_st
