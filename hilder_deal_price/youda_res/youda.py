from dbfread import DBF
from pymongo import MongoClient
import re
import datetime
from lib.log import LogHandler
import yaml
log = LogHandler(__name__)
setting = yaml.load(open('youda_config.yaml'))
mongo = MongoClient(host=setting['mongo_235']['host'],
                    port=setting['mongo_235']['port'],
                    username=setting['mongo_235']['user_name'],
                    password=setting['mongo_235']['password'])
collection = mongo[setting['mongo_235']['db_name']][setting['mongo_235']['collection']]


class Record(object):
    def __init__(self, items):
        for (name, value) in items:
            setattr(self, name, value)

    def insert(self):
        info_dict = self.__dict__
        # 地址格式化，去掉多余室号
        # try:
        #     address = info_dict['CJ_ZL']
        #     delete_room = re.search('(.*号|.*弄|.*幢)', address, re.S | re.M).group(1)
        #     info_dict['CJ_ZL'] = delete_room
        # except Exception as e:
        #     log.error(e)
        #     return
        # # 小区名格式化，多个小区拆分
        # comm_list = []
        # if '、' in info_dict['CJ_LPMC']:
        #     comm_str = info_dict['CJ_LPMC'].split('、')
        #     for i in comm_str:
        #         if '，' in i:
        #             comm_split = i.split('，')
        #             for j in comm_split:
        #                 comm_list.append(j)
        #         else:
        #             comm_list.append(i)
        # elif ',' in info_dict['CJ_LPMC']:
        #     comm_str = info_dict['CJ_LPMC'].split(',')
        #     for i in comm_str:
        #         if '、' in i:
        #             comm_split = i.split('、')
        #             for j in comm_split:
        #                 comm_list.append(j)
        #         else:
        #             comm_list.append(i)
        # else:
        #     comm_list.append(info_dict['CJ_LPMC'])
        # info_dict['CJ_LPMC'] = comm_list
        info_dict.update({'crawler_time': datetime.datetime.now()})
        collection.insert_one(info_dict)
        log.info('插入一条数据{}'.format(info_dict))


if __name__ == '__main__':
    table = DBF('cjxx_3.DBF', recfactory=Record, ignore_missing_memofile=True)
    for record in table:
        record.insert()

