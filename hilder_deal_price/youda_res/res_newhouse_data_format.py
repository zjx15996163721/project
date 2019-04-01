from pymongo import MongoClient
import time
import datetime
import yaml
from BaseClass import Base
setting = yaml.load(open('res_config.yaml'))
crawler = MongoClient(host=setting['mongo_235']['host'],
                      port=setting['mongo_235']['port'],
                      username=setting['mongo_235']['user_name'],
                      password=setting['mongo_235']['password'])
crawler_collection = crawler[setting['mongo_235']['db_name']][setting['mongo_235']['collection_newhouse']]


# 235test  这里测试用２３５的库，以后要换成１３６的库
insert = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
insert_collection = insert['deal_price']['res_newhouse_2018_10_final_test']

# online
# insert = MongoClient(host=setting['mongo_136']['host'],
#                      port=setting['mongo_136']['port'])
# insert_collection = insert[setting['mongo_136']['db_name']][setting['mongo_136']['collection_newhouse']]


class FormatNewHouse(Base):

    def __init__(self, source):
        super(FormatNewHouse, self).__init__(source)
        # 对应字段
        self.corresponding_dict = {
            # 136表字段     # 235抓取表字段
            'block': 'plate',                           # 板块
            'loopPosition': 'module',                   # 环线
            'districtType': 'propertytype',             # 小区类型
            'districtName': 'fullhousingname',          # 小区名
            'premisesName': 'newdiskname',              # 楼盘名称
            'address': 'roadlaneno',                    # 地址
            'contractTime': 'signingdate',              # 签约时间
            'area': 'acreage',                          # 面积
            'region': 'area',                           # 区域
            'price': 'unitprice',                       # 单价（元）
            'totalPrice': 'usd',                        # 总价
            'houseType': 'housetype',                   # 房屋类型
            'houseNature': 'houseproperty',             # 房屋性质
            'floor': 'floor',                           # 楼层
            'houseModel': 'roomtype',                   # 户型
            'makeHouseTime': 'submitteddate',           # 交房时间
            'referencePrice': 'referenceprice',         # 参考单价
            'referenceTotalPrice': 'referenceusd',      # 参考总价
        }

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
            data_dict['flag'] = 0
            insert_collection.insert_one(data_dict)
            print('一条数据入136库 data={}'.format(data_dict))

    # 数据格式化
    def format(self, data):
        new_data = {}
        new_data['resId'] = str(data['_id'])
        new_data['city'] = '上海'

        for key in self.corresponding_dict.keys():
            new_data[key] = data[self.corresponding_dict[key]]

        for u_price in ['price', 'referencePrice']:
            new_data[u_price] = int(float(new_data[u_price]))

        for t_price in ['area', 'totalPrice', 'referenceTotalPrice']:
            new_data[t_price] = float(new_data[t_price])

        new_data['houseType'] = new_data['houseType'].replace(' ', '')
        new_data['houseNature'] = new_data['houseNature'].replace(' ', '')

        # 时间转换
        for revert_time in ['makeHouseTime', 'contractTime']:
            if revert_time in new_data and new_data[revert_time] not in ['', None, 'None']:
                try:
                    final_time = datetime.datetime.strptime(new_data[revert_time].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                except:
                    final_time = datetime.datetime.strptime(new_data[revert_time] + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
                new_data[revert_time] = self.convert_time(final_time)
        self.to_update(new_data)

    def start(self):
        for data in crawler_collection.find(no_cursor_timeout=True):
            self.format(data)


if __name__ == '__main__':
    newhouse = FormatNewHouse('澜斯')
    a = newhouse.convert_time('2018-10-01')
    print(a)
