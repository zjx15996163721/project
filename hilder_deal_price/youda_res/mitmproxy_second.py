from mitmproxy import ctx
from pymongo import MongoClient
import datetime
import json
import yaml
"""
启动方法
虚拟环境 mitmdump -s youda_res/mitmproxy_second.py
"""


def response(flow):

    response = flow.response

    info = ctx.log.info

    # info(str(response.status_code))

    # info(str(response.headers))

    # info(str(response.cookies))

    # info(str(response.text))
    setting = yaml.load(open('res_config.yaml'))

    m = MongoClient(host=setting['mongo_235']['host'],
                    port=setting['mongo_235']['port'],
                    username=setting['mongo_235']['user_name'],
                    password=setting['mongo_235']['password'])
    db = m[setting['mongo_235']['db_name']]
    collection = db[setting['mongo_235']['collection_second']]
    # 二手成交处理数据入235库
    try:
        data_list = json.loads(str(response.text))['data']['sets']['items']
    except Exception as e:
        info('序列化失败,数据格式不标准, e={}'.format(e))
        return
    for data in data_list:
        if not collection.find_one({'area': data['area'], 'plate': data['plate'],
                                    'module': data['module'], 'fullhousingname': data['fullhousingname'],
                                    'newdiskname': data['newdiskname'], 'housingaddressall': data['housingaddressall'],
                                    'unitprice': data['unitprice'], 'acreage': data['acreage'], 'usd': data['usd'],
                                    'housetype': data['housetype'], 'signingdate': data['signingdate'],
                                    'propertytype': data['propertytype'], 'houseaddress': data['houseaddress'],
                                    'housetrait': data['housetrait'], 'submitteddate': data['submitteddate'],
                                    'corporationtype': data['corporationtype']}):
            data.update({'crawler_time': datetime.datetime.now()})
            collection.insert_one(data)
            info('插入一条数据{}'.format(data))
        else:
            info('重复数据')

    """
    去重字段
    area　               区域
    plate　              板块
    module　             环线
    fullhousingname　    小区名称
    newdiskname      　　楼盘名称
    housingaddressall　　地址
    unitprice　          均价
    acreage　　　　　　　  面积
    usd　                总价
    housetype　　　　　　  房屋类型
    signingdate　        签约日期
    propertytype　       小区类型
    houseaddress　       案例地址
    housetrait　         房屋特征
    submitteddate　      竣工日期
    corporationtype　    成交类型
    """
