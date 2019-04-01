"""
统计更新的量
"""
from pymongo import MongoClient
import yaml

setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]


def count():
    count_update_time = 0
    count_crawler_time = 0
    count = 0
    for i in dianping_all_type_collection.find(no_cursor_timeout=True):
        count += 1
        if 'update_time' in i.keys():
            count_update_time += 1
            print('更新的量 {}'.format(count_update_time))
        elif 'crawler_time' in i.keys():
            count_crawler_time += 1
            print('抓取的量 {}'.format(count_crawler_time))
        else:
            print('到{} 个'.format(count))
    print('更新的量 {}'.format(count_update_time))
    print('抓取的量 {}'.format(count_crawler_time))


if __name__ == '__main__':
    count()