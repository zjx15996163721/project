"""
这个文件是处理澜斯的二手成交数据　入到43 fangjia dealprice表中
"""
from BaseClass import Base
from pymongo import MongoClient
import yaml
import requests
import json
from datetime import datetime, timedelta, timezone
from lib.log import LogHandler
log = LogHandler(__name__)
setting = yaml.load(open('res_config.yaml'))
crawler = MongoClient(host=setting['mongo_235']['host'],
                      port=setting['mongo_235']['port'],
                      username=setting['mongo_235']['user_name'],
                      password=setting['mongo_235']['password'])
crawler_collection = crawler[setting['mongo_235']['db_name']][setting['mongo_235']['collection_second']]


class ResData(Base):

    def __init__(self, source):
        super(ResData, self).__init__(source)

    @classmethod
    def match_house_num(cls):
        token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
        url = 'http://open.fangjia.com/address/match'
        count = 0
        for new_data in crawler_collection.find(no_cursor_timeout=True):
            count += 1
            print('到第{}条'.format(count))
            payload = {
                'city': '上海',
                'address': new_data['houseaddress'],
                'category': 'property',
                'token': token
            }
            try:
                r = requests.get(url=url, params=payload)
            except Exception as e:
                log.error(e)
                continue
            text = json.loads(r.text, encoding='utf-8')
            if text['msg'] == 'ok':
                match_new_data = text['result']
                try:
                    crawler_collection.find_one_and_update({'_id': new_data['_id']},
                                                           {'$set': {'fj_house_num': match_new_data['searchAddress']['buildingNumber'],
                                                                     'fj_room_num': match_new_data['searchAddress']['roomNumber'],
                                                                     'fj_floor': match_new_data['searchAddress']['floor']
                                                                     }})
                    print('匹配一条数据的小区 _id={}'.format(new_data['_id']))
                except Exception as e:
                    print('没有匹配数据的小区 _id={}, e={}'.format(new_data['_id'], e))

    def insert_43(self):
        r = ResData('澜斯')
        for data in crawler_collection.find({"fj_flag": 1}, no_cursor_timeout=True):
            if data['propertytype'] in ['住宅', '综合社区', '别墅']:
                r.city = data['fj_city']
                r.region = data['fj_region']
                r.district_name = data['fj_name']
                r.house_num = data.get('fj_house_num', None)
                r.room_num = data.get('fj_room_num', None)
                r.floor = data.get('fj_floor', None)
                if data.get('fj_floor') is not None:
                    r.floor = int(data.get('fj_floor'))
                else:
                    r.floor = None
                if data.get('unitprice') is not None:
                    r.avg_price = int(data.get('unitprice'))
                else:
                    r.avg_price = None
                if data.get('acreage') is not None:
                    r.area = float(data.get('acreage'))
                else:
                    r.area = None
                # 总价＝单价＊面积
                r.total_price = int(r.avg_price * r.area)

                # 转utc时间,减8小时
                r.trade_date = self.local2utc(datetime.strptime(data['signingdate'], "%Y-%m-%d %H:%M:%S"))
                r.m_date = datetime.utcnow().replace(tzinfo=timezone.utc)
                r.packing_space = False
                r.create_date = self.local2utc(data.get('crawler_time', None))
                r.insert_db()


"""
# 43表字段  
'city'                           # 城市
'region'                         # 区域
'district_name'                  # 小区名
'avg_price'                      # 均价 Int 元/平方米
'total_price'                    # 总价 Int 单位元
'house_num'                      # 楼栋号 string
'unit_num'                       # 单元号 string
'room_num'                       # 室号 string
'area'                           # 面积 float
'direction'                      # 朝向
'fitment'                        # 装修
'source'                         # 来源网站
'room'                           # 室数 Int
'hall'                           # 厅数 Int
'toilet'                         # 卫数 Int
'height'                         # 总楼层 Int
'floor'                          # 所在楼层 Int
'trade_date'                     # 交易时间
'm_date'                         # 更新时间
'create_date'                    # 创建时间
'packing_space'                  # 添加标记，默认为False,如果有地下或者车位的改为True
'url': ''                        # 链接
"""
