from BaseClass import Base
from pymongo import MongoClient
import yaml
from datetime import datetime
from lib.standardization import StandardCity
from lib.log import LogHandler
log = LogHandler(__name__)
setting = yaml.load(open('config_local.yaml'))
m = MongoClient(host=setting['mongo_235']['host'],
                port=setting['mongo_235']['port'],
                username=setting['mongo_235']['user_name'],
                password=setting['mongo_235']['password'])
# 235数据库 deal_price lianjiazaixian
db = m[setting['mongo_235']['db_name']]
crawler_collection = db[setting['mongo_235']['coll_comm']]

"""
城市              city               str
区域              region             str
房产面积，         area               float
户型，            main_type          str
物业类型，         estate_type2       str
装修情况，         fitment            str
朝向，            direction          str
建成年代，         create_year        str
挂牌价，          listing_price       int
成交周期，         deal_cycle         str
成交时间，        trade_date          date
挂牌时间，         listing_date       date
地址，            address            str
小区，            district_name      str
调价次数，         adjust_price_count int
成交价格，  单价    avg_price       int 元/平方米
         总价     total_price     int 单位元
配备电梯，         elevator_configuration       Ture / Flase
数据来源，          source              str
获得时间。         create_date          date
"""


class Child(Base):

    def __init__(self, main_type=None, estate_type2=None, create_year=None, listing_price=None,
                 deal_cycle=None, listing_date=None, adjust_price_count=None, elevator_configuration=None, address=None, url=None):
        self.main_type = main_type          # 户型      str
        self.estate_type2 = estate_type2    # 物业类型   str
        self.create_year = create_year      # 建成年代   str
        self.listing_price = listing_price  # 挂牌价     int
        self.deal_cycle = deal_cycle        # 成交周期   str
        self.listing_date = listing_date    # 挂牌时间   date
        self.adjust_price_count = adjust_price_count  # 调价次数 int
        self.address = address              # 地址     str
        self.elevator_configuration = elevator_configuration  # 配备电梯  Ture / Flase
        self.create_date = datetime.utcnow()   # 创建时间
        self.url = url

    def insert_db(self):
        data = self.serialization_info(self)
        try:
            self.check_data_validity(data)
        except Exception as e:
            log.error(e)
            return
        standard = StandardCity()
        city_success, data['city'] = standard.standard_city(data['city'])
        region_success, data['region'] = standard.standard_region(data['city'], data['region'])
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
            log.info('一条数据入235库={}'.format(data))
            return True
        else:
            log.info('已经存在数据={}'.format(data))
            return True





