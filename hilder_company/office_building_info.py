import datetime
import yaml
from lib.log import LogHandler
from pymongo import MongoClient
from lib.standardization import standard_city, standard_region
from pymongo.errors import DuplicateKeyError

"""
城市 区域 名称 cat + 价格去重
"""

log = LogHandler(__name__)

setting = yaml.load(open('config.yaml', encoding='UTF-8'))
client = MongoClient(host=setting['mongo']['host'],
                     port=setting['mongo']['port'],
                     username=setting['mongo']['user_name'],
                     password=setting['mongo']['password'])
db = client[setting['mongo']['db']]
collection = db[setting['mongo']['collection']]


class OfficeBuilding:
    def __init__(self, source, city=None, region=None, name=None, alias=None, address=None,
                 developer=None, estate_charge=None, estate_company=None, bed_kind=None,
                 cubage_percent=None,build_area=None,all_area=None, floor_info=None, fitment=None,
                 elevator_brand=None, car_site_count=None,characteristic=None,conditioner_time=None,
                 person_elevators_count=None,goods_elevator_count=None, land_car_site=None,
                 underground_car_site=None,parking_fee=None, safe_system=None, network_way=None,
                 clear_height=None, standard_height=None, standard_area=None, lobby_height=None,
                 is_foreign=None, is_register=None, build_facilities=None, delivery_level=None,
                 property_life=None, block=None, payment_pattern=None, virescence_percent=None,
                 build_type=None, elevators_count=None, facilities=None,traffic=None, live_date=None,
                 licence=None,finish_building_date=None, fitment_level=None, build_designer=None,
                 cons_company=None, metro_info=None, open_date=None,divisible=None, surrounding=None,
                 business_quarter=None,loop_line_info=None, rent_type=None, bay_area=None, addr_alias=None,
                 intelligence_level=None, total_floor=None, meeting_room=None, real_use_percent=None,
                 office_type=None, sell_type=None, car_site_description=None, rent_property_life=None,
                 is_regular_bus=None,regular_bus_time=None, conditioner=None, conditioner_add_time=None,
                 metro_station_name=None,estate_info=None, lng=None, lat=None, lng2=None, lat2=None, lng3=None, lat3=None,url=None):

        self.cat = 'office'
        self.source = source  # 来源
        self.city = city  # 城市   string
        self.region = region  # 区域 string
        self.name = name  # 名称 string
        self.alias = alias  # 别名 list
        self.address = address  # 地址 string
        self.addr_alias = addr_alias  # 地址别名  list
        self.bed_kind = bed_kind  # 写字楼等级  string
        self.office_type = office_type  # 写字楼类型
        self.build_type = build_type  # 建筑类型  string
        self.block = block  # 板块  string
        self.business_quarter = business_quarter  # 商圈  string
        self.loop_line_info = loop_line_info  # 环线位置  string
        self.intelligence_level = intelligence_level  # 智能水平  string
        self.licence = licence  # 预售许可证  string
        self.characteristic = characteristic  # 项目特色  string
        self.total_floor = total_floor  # 总楼层  string
        self.meeting_room = meeting_room  # 会议室  string
        self.live_date = live_date  # 入住时间  string
        self.divisible = divisible  # 是否可分割  integer
        self.real_use_percent = real_use_percent  # 得房率  string
        self.delivery_level = delivery_level  # 交房标准  string
        self.build_facilities = build_facilities  # 楼内配套  string
        self.build_designer = build_designer  # 设计单位  string
        self.cons_company = cons_company  # 施工单位  string
        self.rent_type = rent_type  # 出租类型  string
        self.sell_type = sell_type  # 出售类型  string
        self.rent_property_life = rent_property_life  # 租赁年限  string
        self.payment_pattern = payment_pattern  # 付款方式  string
        self.estate_charge = estate_charge  # 物业费 string
        self.car_site_count = car_site_count  # 停车位数  integer
        self.car_site_description = car_site_description  # 车位描述 string
        self.land_car_site = land_car_site  # 地上车位数  string
        self.underground_car_site = underground_car_site  # 地下车位数  string
        self.parking_fee = parking_fee  # 车位月租金  string
        self.bay_area = bay_area  # 开间面积  string
        self.property_life = property_life  # 产权年限  string
        self.floor_info = floor_info  # 楼层状况  string
        self.clear_height = clear_height  # 净高  string
        self.standard_height = standard_height  # 标准层高  string
        self.standard_area = standard_area  # 标准层面积  string
        self.lobby_height = lobby_height  # 大堂层高  string
        self.is_foreign = is_foreign  # 是否涉外  string
        self.is_register = is_register  # 是否可注册 string
        self.is_regular_bus = is_regular_bus  # 是否有班车
        self.regular_bus_time = regular_bus_time  # 班车时间
        self.conditioner = conditioner  # 空调
        self.conditioner_time = conditioner_time  # 空调开放时间  string
        self.conditioner_add_time = conditioner_add_time  # 空调加时
        self.elevators_count = elevators_count  # 电梯数量  string
        self.elevator_brand = elevator_brand  # 电梯品牌  string
        self.person_elevators_count = person_elevators_count  # 客梯数  string
        self.goods_elevator_count = goods_elevator_count  # 货梯数 string
        self.fitment = fitment  # 装修状况 string
        self.open_date = open_date  # 开盘时间  date
        self.finish_building_date = finish_building_date  # 竣工时间  string
        self.all_area = all_area  # 占地面积 string
        self.cubage_percent = cubage_percent  # 容积率 string
        self.build_area = build_area  # 建筑面积 string
        self.virescence_percent = virescence_percent  # 绿化率  string
        self.developer = developer  # 开发商  string
        self.estate_company = estate_company  # 物业公司 string
        self.safe_system = safe_system  # 安防系统  string
        self.network_way = network_way  # 网络通讯  string
        self.metro_info = metro_info  # 地铁沿线  string
        self.fitment_level = fitment_level  # 装修标准  string
        self.metro_station_name = metro_station_name  # 地铁站名
        self.surrounding = surrounding  # 周边配套  string
        self.facilities = facilities  # 配套设施  string
        self.traffic = traffic  # 交通状况  string
        self.estate_info = estate_info  # 物业概况 string
        self.lng = lng    # 经度 string 高德
        self.lat = lat    # 纬度 string 高德
        self.lng2 = lng2  # 经度 string 百度
        self.lat2 = lat2  # 纬度 string 百度
        self.lng3 = lng3  # 经度 string 腾讯
        self.lat3 = lat3  # 纬度 string 腾讯
        self.url = url

    def serialization_info(self):
        """
        :param info:
        :return: data:
        """
        return {key: value for key, value in vars(self).items()}


    def insert_db(self):
        data = self.serialization_info()
        data['crawler_time'] = datetime.datetime.now()
        try:
            if collection.find_one(
                    {'source': data['source'], 'city': data['city'], 'region': data['region'], 'name': data['name'],
                     'cat': data['cat']}) is None:
                collection.insert_one(data)
                log.info('插入数据={}'.format(data))
            else:
                log.info('重复数据={}'.format(data))
        except DuplicateKeyError as e:
            log.error(e)

        # # 格式化城市区域
        # result, real_city = standard_city(data['city'])
        # result_, real_region = standard_region(data['city'], data['region'])
        # if result and result_:
        #     data['city'] = real_city
        #     data['region'] = real_region
        #     try:
        #         if collection.find_one(
        #                 {'source': data['source'],'city': data['city'], 'region': data['region'], 'name': data['name'], 'cat': data['cat']}) is None:
        #             collection.insert_one(data)
        #             log.info('插入数据={}'.format(data))
        #         else:
        #             log.info('重复数据={}'.format(data))
        #     except DuplicateKeyError as e:
        #         log.error(e)


