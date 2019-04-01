from pymongo import MongoClient
import datetime
from BaseClass import Base
from lib.log import LogHandler
import yaml
import re
from lib.match_district import match
from datetime import datetime, timedelta, timezone
log = LogHandler(__name__)
setting = yaml.load(open('youda_config.yaml'))
mongo = MongoClient(host=setting['mongo_235']['host'],
                    port=setting['mongo_235']['port'],
                    username=setting['mongo_235']['user_name'],
                    password=setting['mongo_235']['password'])
crawler_collection = mongo[setting['mongo_235']['db_name']][setting['mongo_235']['collection']]

match_collection = mongo[setting['mongo_235']['match_db']][setting['mongo_235']['collection_youda_res_xzj']]


class YouData(Base):

    def __init__(self, source):
        super(YouData, self).__init__(source)

    @staticmethod
    def format():
        for info_dict in crawler_collection.find(no_cursor_timeout=True):
            _id = info_dict['_id']
            # 地址格式化，去掉多余室号
            try:
                address = info_dict['CJ_ZL']
                delete_room = re.search('(.*号|.*弄|.*幢)', address, re.S | re.M).group(1)
                # info_dict['address'] = delete_room
                crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'address': delete_room}})
                print('去除室号_id={}, {}'.format(_id, delete_room))
            except Exception as e:
                log.error(e)

            # 小区名格式化，多个小区拆分
            comm_list = []
            if '、' in info_dict['CJ_LPMC']:
                comm_str = info_dict['CJ_LPMC'].split('、')
                for i in comm_str:
                    if '，' in i:
                        comm_split = i.split('，')
                        for j in comm_split:
                            comm_list.append(j)
                    else:
                        comm_list.append(i)
            elif ',' in info_dict['CJ_LPMC']:
                comm_str = info_dict['CJ_LPMC'].split(',')
                for i in comm_str:
                    if '、' in i:
                        comm_split = i.split('、')
                        for j in comm_split:
                            comm_list.append(j)
                    else:
                        comm_list.append(i)
            else:
                comm_list.append(info_dict['CJ_LPMC'])
            # info_dict['name_list'] = comm_list
            crawler_collection.find_one_and_update({'_id': _id}, {'$set': {'name_list': comm_list}})
            print('小区名称切分{}'.format(comm_list))

    @staticmethod
    def match():
        # 先到匹配表里查 找不到再跑接口匹配
        for i in crawler_collection.find(no_cursor_timeout=True):
            source = 'youda'
            city = '上海'
            region = i['CJ_XQ']
            friendsName = i['CJ_LPMC']
            data = match_collection.find_one({'source': source, 'city': city, 'region': region, 'friendsName': friendsName})
            if data:
                crawler_collection.find_one_and_update({'_id': i['_id']}, {'$set': {'fj_city': data['city'],
                                                                                    'fj_region': data['region'],
                                                                                    'fj_name': data['fjName'],
                                                                                    'fj_flag': 1,
                                                                                    'update_time': datetime.utcnow()}})
                log.info('更新数据 _id={}'.format(i['_id']))
            else:
                friendsAddress = i['CJ_ZL']
                address = re.search('\d+(号|弄|支|支弄|单号|双号|甲号|乙号|丙号|丁号)', friendsAddress, re.S | re.M)
                if address:
                    data = match_collection.find_one({'source': source, 'city': city, 'region': region, 'friendsAddress': friendsAddress})
                    if data:
                        crawler_collection.find_one_and_update({'_id': i['_id']},{'$set': {'fj_city': data['city'],
                                                                                           'fj_region': data['region'],
                                                                                           'fj_name': data['fjName'],
                                                                                           'fj_flag': 1,
                                                                                           'update_time': datetime.utcnow()}})
                        log.info('更新数据 _id={}'.format(i['_id']))

        for j in crawler_collection.find({'fj_flag': None}, no_cursor_timeout=True):
            if j['CJ_FWYT'] in ['住宅', '综合社区', '别墅', '里弄房', '老公房']:
                city = '上海'
                region = j['CJ_XQ']
                friendsName = j['name_list']
                for name in friendsName:
                    data = match(city=city, region=region, keyword=name)
                    if data:
                        if data['flag'] == '精确匹配':
                            crawler_collection.find_one_and_update({'_id': j['_id']}, {'$set': {'fj_city': data['mcity'],
                                                                                                'fj_region': data['mregion'],
                                                                                                'fj_name': data['mname'],
                                                                                                'fj_flag': 1,
                                                                                                'update_time': datetime.utcnow().replace(tzinfo=timezone.utc)}})
                            log.info('更新数据 _id={}'.format(j['_id']))
                            break

        for k in crawler_collection.find({'fj_flag': None}, no_cursor_timeout=True):
            if k['CJ_FWYT'] in ['住宅', '综合社区', '别墅', '里弄房', '老公房']:
                city = '上海'
                region = k['CJ_XQ']
                if 'address' in k:
                    data = match(city=city, region=region, keyword=k['address'])
                    if data:
                        if data['flag'] == '精确匹配':
                            crawler_collection.find_one_and_update({'_id': k['_id']}, {'$set': {'fj_city': data['mcity'],
                                                                                                'fj_region': data['mregion'],
                                                                                                'fj_name': data['mname'],
                                                                                                'fj_flag': 1,
                                                                                                'update_time': datetime.utcnow().replace(tzinfo=timezone.utc)}})
                            log.info('更新数据 _id={}'.format(k['_id']))

    @staticmethod
    def insert_43():
        y = YouData('友达')
        for data in crawler_collection.find({"fj_flag": 1}, no_cursor_timeout=True):
            y.city = data['fj_city']
            y.region = data['fj_region']
            y.district_name = data['fj_name']
            y.avg_price = int(data['CJ_CJDJ'])
            y.total_price = int(int(data['CJ_CJDJ']) * float(data['CJ_JZMJ']))
            y.area = float(data['CJ_JZMJ'])
            y.direction = data['CJ_CX']
            y.trade_date = y.local2utc(data['CJ_CJRQ'])
            y.m_date = datetime.utcnow()
            y.create_date = y.local2utc(data['crawler_time'])
            y.insert_db()


"""
字段：

CJ_XH                序号
CJ_XQ　　　　　　　　区域
CJ_XXLB　            板块
CJ_HXWZ　            环线位置
CJ_ZL　　　　　　　　地址
CJ_LPMC             　小区名称
CJ_FWLX             　房屋类型
CJ_CX　　　　　　　　朝向
CJ_FWYT             　房屋用途
CJ_SYQX             　使用期限
CJ_TDQBFS           　土地取得方式
SRRQ　　　　　　　　　输入日期
XGSJ            　　　修改时间
CJ_JZMJ　　　　　　　　建筑面积
CJ_CJDJ             　成交单价
CJ_CJRQ　　　　　　　　成交日期
CJ_CJJG                成交价格
CJR　　　　　　　　　　输入人员
CJ_JGRQ               竣工日期
CJ_SHBW         　　　室号部位
CJ_FWJG             　房屋结构
CJ_TDYT　　　　　　　　土地用途
CJ_TDMJ　　　　　　　　土地面积
CJ_CS                   层数
"""
