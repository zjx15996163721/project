from pymongo import MongoClient
from lib.log import LogHandler
import yaml
log = LogHandler('wangyi')
setting = yaml.load(open('wangyi_config.yaml'))
m = MongoClient(host=setting['mongo_235']['host'],
                port=setting['mongo_235']['port'],
                username=setting['mongo_235']['user_name'],
                password=setting['mongo_235']['password'])
crawler_collection = m[setting['mongo_235']['db_name']][setting['mongo_235']['collection']]

n = MongoClient(host=setting['mongo_136']['host'], port=setting['mongo_136']['port'])
insert_collection = n[setting['mongo_136']['db_name']][setting['mongo_136']['collection']]


def insert_136():
    count = 0
    for data in crawler_collection.find(no_cursor_timeout=True):
        count += 1
        print('到第{}条'.format(count))
        if not insert_collection.find_one({'city': data['city'], 'region': data['region'], 'name': data['name'],
                                           'resource': data['resource'], 'house_num': data['house_num'],
                                           'total_size': data['total_size'], 'avg_price': data['avg_price'],
                                           'total_price': data['total_price'], 'date': data['date'],
                                           'his_num': data['his_num'], 'his_size': data['his_size'],
                                           'not_sale_num': data['not_sale_num'], 'not_sale_size': data['not_sale_size']}):
            insert_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            log.info('重复数据')


"""
city        城市　     string
region      区域　     string
name        小区名　   string
house_num   成交量     int
total_size  成交总面积 int
total_price 总价　     long
avg_price   均价　     int
date        成交日期　 Date
his_num     历史成交数 int
his_size    历史成交面积int
not_sale_num 未售数量　int
not_sale_size 未售面积　int
resource    来源      　string
c_date      创建时间　  date
"""
