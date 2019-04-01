from dataclasses import dataclass, asdict, field
import datetime
import yaml
from lib.log import LogHandler
from lib.mongo import Mongo

log = LogHandler(__name__)

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'],
               port=setting['mongo']['port'],
               user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
soldcoll = client[setting['mongo']['db']][setting['mongo']['collection_1']]
listcoll = client[setting['mongo']['db']][setting['mongo']['collection_2']]
rentcoll = client[setting['mongo']['db']][setting['mongo']['collection_3']]


@dataclass()
class Estate:
    co_id: str   # 小区id
    source: str  # 网站来源
    state: str  # 州
    county: str  # 州下一级行政区
    city: str  # 市
    zipcode: str  # 邮编
    # street_number: str      # 街道号码
    # street: str             # 街道名
    # apartment_number: str    # 门牌号
    address: str  # 地址
    house_type: str  # 房屋类型
    size: str  # 使用面积
    lot_size: str  # 占地面积
    year_built: str  # 建成年份
    beds: str  # 卧室
    baths: str  # 浴室卫生间
    # floor: int              # 所在楼层
    # total_floor: int        # 总楼层
    hoafee: str  # 物业费
    agent_name: str  # 中介人名称
    agent_phone: str  # 中介电话


@dataclass
class SoldPrice(Estate):
    price: str
    avg_price: str
    deal_date: str

    def soldprice_insert(self):
        if soldcoll.find_one({'co_id':self.co_id}):
            print('{}已存在'.format(self.co_id))
        else:
            soldcoll.insert_one(asdict(self))

            log.info('已插入soldprice数据{}'.format(asdict(self)))


@dataclass
class ListedPrice(Estate):
    price: str
    avg_price: str
    listed_date: str

    def listprice_insert(self):
        if listcoll.find_one({'co_id':self.co_id}):
            print('{}已存在'.format(self.co_id))
        else:
            listcoll.insert_one(asdict(self))
            listcoll.ensure_index()
            log.info('已插入listprice数据{}'.format(asdict(self)))


@dataclass
class RentPrice(Estate):
    room_name: str
    size: str
    price: str
    beds: str
    baths: str
    available_date: str
    property_phone: str

    def rentprice_insert(self):
        if rentcoll.find_one({'co_id':self.co_id}):
            print('{}已存在'.format(self.co_id))
        else:
            rentcoll.insert_one(asdict(self))
            log.info('已插入rentprice数据{}'.format(asdict(self)))


if __name__ == '__main__':
    s = SoldPrice(price=100.0, avg_price=1000.0, deal_date='2018', state=None)
    s.soldprice_insert()
