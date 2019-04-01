from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

# 创建对象的基类
Base = declarative_base()
top_city_list = ['上海', '北京', '广州', '深圳', '天津',
                 '无锡', '西安', '武汉', '大连', '宁波',
                 '南京', '沈阳', '苏州', '青岛', '长沙',
                 '成都', '重庆', '杭州', '厦门']
extra_city = '合肥'

# 58同城权重是最高的
source = ['链家', '58同城', '房估估', '安居客', '房天下']


class District:
    def __init__(self, estate_charge, complete_time, house_hold_count, region, city, address, district_name):
        self.estate_charge = estate_charge  # 物业费
        self.complete_time = complete_time  # 竣工时间
        self.house_hold_count = house_hold_count  # 户数
        self.district_name = district_name
        self.address = address
        self.region = region
        self.city = city
        self.source = source


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    city_name = Column(String(2000))


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)
    source_name = Column(String(2000))
    source = Column(Integer)


class CitySource(Base):
    __tablename__ = 'city_source'

    id = Column(Integer, primary_key=True)
    url = Column(String(2000))
    request_parameter = Column(String(2000))
    city_id = Column(Integer)
    source_id = Column(Integer)
