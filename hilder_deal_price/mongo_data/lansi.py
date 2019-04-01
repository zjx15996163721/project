"""
给组长的一句话：因为不知道这数据是干嘛的，，所以我直接放到数据库，没有进行去重操作
"""

from pymongo import MongoClient
import yaml
from deal_price_info import Comm
import datetime
import re
from lib.log import LogHandler
import time

log = LogHandler(__name__)
setting = yaml.load(open('config_local.yaml'))
mongo_setting = setting['mongo']
# 链接235数据库
client = MongoClient(host=mongo_setting['host'],
                     port=mongo_setting['port'],
                     username=mongo_setting['user_name'],
                     password=mongo_setting['password'])

# 这一个数据表我是在235数据库中进行测试使用的，，组长跑线上的时候只需要修改配置文件就好
put_collection = client[mongo_setting['db_name']][mongo_setting['coll_comm']]

# 数据读取表所在的数据库
read_db = client['deal_price']

'''
组长：以下三个函数分别是读取三张表格入库，因为表格不一样，连接也不一样，所以写成函数方便看
'''


# 入库函数
def into_mongo(coll):
    com = Comm('澜斯')
    results = coll.find(no_cursor_timeout=True)
    for result in results:
        # 这个地方写一个try是因为我再测试的时候发现有的木有fj_city
        try:
            com.city = result['fj_city']  # 城市
            com.region = result['fj_region']  # 区域
        except Exception as e:
            log.error('城市或者区域没有')

        com.m_date = result['updatedate']  # 更新日期
        com.create_date = datetime.datetime.now()  # 创建时间
        com.fitment = result['newdiskdecoration']  # 装修
        com.floor = result['flevel']  # 所在楼层

        # try是因为在插入数据库中这几个如果不符合，就不会插入
        try:
            com.district_name = result['fj_name']  # 小区名称
            com.avg_price = result['unitprice']  # 单价
            com.total_price = result['usd']  # 总价
            com.area = result['acreage']  # 面积=建筑面积

            t = time.strptime(result['signingdate'].split('T')[0], "%Y-%m-%d")
            y = t.tm_year
            m = t.tm_mon
            d = t.tm_mday
            com.trade_date = datetime.datetime(y, m, d)

        except Exception as e:
            log.error(e)

        # 这一部分我写了正则从地址中匹配单元号和室号，如果组长感觉不对，，直接注释掉就好
        houseaddress = result['houseaddress']
        try:
            res = re.search('(\d+)号(\d+)', houseaddress)
            com.unit_num = res.group(1)  # 单元号
            com.room_num = res.group(2)  # 室号
        except Exception as e:
            print('无法匹配大盘单元号和室号，houseaddress={}'.find(houseaddress))

        # 以下数据库确定无法匹配,写上是为了让您看看
        # com.direction = None  # 朝向
        # com.room = None  # 室数
        # com.hall = None  # 厅数
        # com.toilet = None  # 卫数
        # com.height = None  # 总楼层
        # com.house_num = None  # 楼栋号

        # 执行插入操作
        com.insert_db()


# 读取第一张表
def read_one():
    read_connection1 = read_db['res_second_1949_2012']
    into_mongo(read_connection1)


# 读取第二张表
def read_two():
    read_connection2 = read_db['res_second_2017']
    into_mongo(read_connection2)


# 读取第三张表
def read_three():
    read_connection3 = read_db['res_second_2012_2017']
    into_mongo(read_connection3)


if __name__ == '__main__':
    # 读取第一张表入库
    read_one()

    # 读取第二张表入库
    read_two()

    # #读取第三张表入库
    read_three()
