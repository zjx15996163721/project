from pymongo import MongoClient
import re
import yaml
import requests
import json
from collections import Counter
from lib.match_district import match
from datetime import datetime, timezone
from BaseClass import Base
setting = yaml.load(open('res_config.yaml'))
crawler = MongoClient(host=setting['mongo_235']['host'],
                      port=setting['mongo_235']['port'],
                      username=setting['mongo_235']['user_name'],
                      password=setting['mongo_235']['password'])
crawler_collection = crawler[setting['mongo_235']['db_name']][setting['mongo_235']['collection_second']]
collection_match = crawler[setting['mongo_235']['match_db']][setting['mongo_235']['collection_youda_res_xzj']]
collection_house_loudong = crawler[setting['mongo_235']['loudong_db']][setting['mongo_235']['collection_house_loudong']]

insert = MongoClient(host=setting['mongo_136']['host'],
                     port=setting['mongo_136']['port'])
insert_collection = insert[setting['mongo_136']['db_name']][setting['mongo_136']['collection_second']]
collection_seaweed = insert[setting['mongo_136']['db_fangjia']][setting['mongo_136']['collection_seaweed']]


class FormatSecond(Base):

    def __init__(self, source):
        super(FormatSecond, self).__init__(source)
        # 对应字段
        self.corresponding_dict = {
            # 136表字段     # 235抓取表字段
            'block': 'plate',                     # 板块
            'loopPosition': 'module',             # 环线
            'districtType': 'propertytype',       # 小区类型
            'districtName': 'fullhousingname',    # 小区名
            'premisesName': 'newdiskname',        # 楼盘名称
            'address': 'houseaddress',            # 地址  #
            'contractTime': 'signingdate',        # 签约时间
            'area': 'acreage',                    # 面积
            'region': 'area',                     # 区域
            'price': 'unitprice',                 # 单价（元）
            'totalPrice': 'usd',                  # 总价
            'houseType': 'housetype',             # 房屋类型
            'houseFeatures': 'housetrait',        # 房屋特征
            'makeHouseTime': 'registerdate',      # 交房时间
            'completedTime': 'submitteddate',     # 竣工时间
            'transactionType': 'corporationtype', # 成交类型
            'floor': 'floor',                     # 楼层 int
            'totalFloor': 'totalFloor',           # 总楼层 int
            'lng': 'lng',                         # 经纬度 float
            'lat': 'lat',
            'location': 'location',               # 坐标 str 比如：31.964981,118.716736
            'fjCity': 'fj_city',                  # 格式化化城市
            'fjRegion': 'fj_region',              # 格式化区域
            'fjName': 'fj_name',                  # 格式化小区名
        }
        self.count = 0

    # 数据更新、入库
    def to_update(self, data_dict):

        # 查看表中是否存在，存在则更新，不存在则入库
        one_data = insert_collection.find_one({'address': data_dict['address'], 'contractTime': data_dict['contractTime'],
                                               'region': data_dict['region'], 'area': data_dict['area'],
                                               'totalPrice': data_dict['totalPrice']})
        update_dict = {}
        if one_data:
            for data in data_dict.keys():
                if data not in one_data.keys() or one_data[data] in ['', None, 0.0, 0, '0', '0.0']:
                    update_dict[data] = data_dict[data]
            update_dict['flag'] = 1
            if len(update_dict) > 1:
                insert_collection.update({'_id': one_data['_id']}, {'$set': update_dict})
                print('更新一条数据 data={}'.format(update_dict))
        else:
            # data_dict['flag'] = 0
            insert_collection.insert_one(data_dict)
            print('一条数据入136库 data={}'.format(data_dict))
            self.count += 1

    # 数据格式化
    def format(self, data):
        new_data = {}
        new_data['resId'] = str(data['_id'])
        new_data['city'] = '上海'

        for key in self.corresponding_dict.keys():
            new_data[key] = data[self.corresponding_dict[key]]

        new_data['price'] = int(float(new_data['price']))
        new_data['area'] = float(new_data['area'])
        new_data['totalPrice'] = float(new_data['totalPrice']/10000)
        new_data['houseType'] = new_data['houseType'].replace(' ', '')

        # 时间转换,调用Base父类方法,转UTC时间，减８小时
        for revert_time in ['makeHouseTime', 'contractTime', 'completedTime']:
            if revert_time in new_data and new_data[revert_time] not in ['', None, 'None']:
                try:
                    final_time = datetime.strptime(new_data[revert_time].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                except:
                    final_time = datetime.strptime(new_data[revert_time] + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
                new_data[revert_time] = self.local2utc(final_time)
        self.to_update(new_data)

    @staticmethod
    def add_fj_name():
        # 先到匹配表里查 找不到再跑接口匹配
        for i in crawler_collection.find(no_cursor_timeout=True):
            source = 'res'
            city = '上海'
            region = i['area']
            friendsName = i['fullhousingname']
            data = collection_match.find_one({'source': source, 'city': city, 'region': region, 'friendsName': friendsName})
            if data:
                crawler_collection.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': data['city'],
                                                                                    'fj_region': data['region'],
                                                                                    'fj_name': data['fjName'],
                                                                                    'fj_flag': 1,
                                                                                    'update_time': datetime.utcnow()}})
                print('更新数据 添加格式化城市区域小区名 _id={}'.format(data['_id']))
            else:
                friendsAddress = i['housingaddressall']
                address = re.search('\d+(号|弄|支|支弄|单号|双号|甲号|乙号|丙号|丁号)', friendsAddress, re.S | re.M)
                if address:
                    data = collection_match.find_one({'source': source, 'city': city, 'region': region, 'friendsAddress': friendsAddress})
                    if data:
                        crawler_collection.find_one_and_update({'_id': i['_id']},
                                                               {'$set': {'fj_city': data['city'],
                                                                         'fj_region': data['region'],
                                                                         'fj_name': data['fjName'],
                                                                         'fj_flag': 1,
                                                                         'update_time': datetime.utcnow().replace(tzinfo=timezone.utc)}})
                        print('更新数据 添加格式化城市区域小区名 _id={}'.format(data['_id']))

        for j in crawler_collection.find({'fj_flag': None}, no_cursor_timeout=True):
            if j['propertytype'] in ['住宅', '综合社区', '别墅']:
                city = '上海'
                region = j['area']
                """
                取两个字段相同的部分为小区名
                """
                fullhousingname = j['fullhousingname']
                newdiskname = j['newdiskname']
                Counter(fullhousingname)
                Counter(newdiskname)
                c = Counter(fullhousingname) & Counter(newdiskname)
                friendsName = "".join(c.keys())

                data = match(city=city, region=region, keyword=friendsName)
                if data:
                    if data['flag'] == '精确匹配':
                        crawler_collection.find_one_and_update({'_id': j['_id']}, {'$set': {'fj_city': data['mcity'],
                                                                                            'fj_region': data['mregion'],
                                                                                            'fj_name': data['mname'],
                                                                                            'fj_flag': 1,
                                                                                            'update_time': datetime.utcnow()}})
                        print('更新数据 _id={}'.format(j['_id']))
                else:
                    friendsAddress = j['houseaddress']
                    data = match(city=city, region=region, keyword=friendsAddress)
                    if data:
                        if data['flag'] == '精确匹配':
                            crawler_collection.find_one_and_update({'_id': j['_id']}, {'$set': {'fj_city': data['mcity'],
                                                                                                'fj_region': data['mregion'],
                                                                                                'fj_name': data['mname'],
                                                                                                'fj_flag': 1,
                                                                                                'update_time': datetime.utcnow()}})
                            print('更新数据 _id={}'.format(j['_id']))

    @staticmethod
    def add_lng():
        for i in crawler_collection.find({'fj_flag': 1}, no_cursor_timeout=True):
            data = collection_seaweed.find_one({'cat': 'district', 'status': 0,
                                                'city': i['fj_city'],
                                                'region': i['fj_region'],
                                                'name': i['fj_name']})
            if data and 'lng2' in data:
                lng = float(data['lng2'] / 10 ** 10)
                lat = float(data['lat2'] / 10 ** 10)
                location = str(lat) + ',' + str(lng)
                crawler_collection.find_one_and_update({'_id': i['_id']}, {'$set': {'lng': lng, 'lat': lat, 'location': location}})
                print('_id={},更新经纬度{}'.format(i['_id'], location))
            else:
                crawler_collection.find_one_and_update({'_id': i['_id']},
                                                       {'$set': {'lng': None, 'lat': None, 'location': None}})
                print('_id={},没有经纬度'.format(i['_id']))

    @staticmethod
    def add_floor():
        for i in crawler_collection.find({'fj_flag': 1}, no_cursor_timeout=True):
            token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
            url = 'http://open.fangjia.com/address/match'
            _id = i['_id']
            payload = {
                'city': '上海',
                'address': i['houseaddress'],
                'category': 'property',
                'token': token
            }
            try:
                r = requests.get(url=url, params=payload, timeout=60)
            except Exception as e:
                print(e)
                return
            text = json.loads(r.text, encoding='utf-8')
            if text['msg'] == 'ok':
                data = text['result']
                if 'floor' in data['searchAddress']:
                    floor = data['searchAddress']['floor']
                    try:
                        if '-' in floor:
                            floor = int(floor.split('-')[0])
                        else:
                            floor = int(floor)
                    except Exception as e:
                        print(e)
                        floor = None
                else:
                    floor = None
                crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'floor': floor}})
                print('_id={},更新楼层{}'.format(_id, floor))
                house_num = data['searchAddress'].get('buildingNumber', None)
                room_num = data['searchAddress'].get('roomNumber', None)
                unitNumber = data['searchAddress'].get('unitNumber', '--')
                loudong_name = collection_house_loudong.find_one({'city': i['fj_city'], 'region': i['fj_region'],
                                                                  'name': i['fj_name'], 'house_num': house_num,
                                                                  'house_num_unit': unitNumber, 'room_num': room_num})
                loudong_name_in_seaweed = collection_house_loudong.find_one({'city': i['fj_city'],
                                                                             'region': i['fj_region'],
                                                                             'name_in_seaweed': i['fj_name'],
                                                                             'house_num': house_num,
                                                                             'house_num_unit': unitNumber,
                                                                             'room_num': room_num})

                if loudong_name and 'all_floor' in loudong_name:
                    totalFloor = loudong_name['all_floor']
                    if totalFloor in [0, -1, None]:
                        crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                        print('_id={},更新总楼层{}'.format(_id, None))
                    else:
                        totalFloor = int(totalFloor)
                        crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': totalFloor}})
                        print('_id={},更新总楼层{}'.format(_id, totalFloor))
                elif loudong_name_in_seaweed and 'all_floor' in loudong_name_in_seaweed:
                    totalFloor = loudong_name_in_seaweed['all_floor']
                    if totalFloor in [0, -1, None]:
                        crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                        print('_id={},更新总楼层{}'.format(_id, None))
                    else:
                        totalFloor = int(totalFloor)
                        crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': totalFloor}})
                        print('_id={},更新总楼层{}'.format(_id, totalFloor))
                else:
                    crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'totalFloor': None}})
                    print('_id={},更新总楼层{}'.format(_id, None))

    def insert_136(self):
        for data in crawler_collection.find({'fj_flag': 1}, no_cursor_timeout=True):
            self.format(data)
        print('{}条数据入136 res_esfdealprice表'.format(self.count))


if __name__ == '__main__':
    f = FormatSecond('澜斯')
    f.insert_136()
