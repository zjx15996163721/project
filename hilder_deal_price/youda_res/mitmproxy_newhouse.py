from mitmproxy import ctx
from pymongo import MongoClient
import datetime
import json
import yaml
"""
启动方法
虚拟环境 mitmdump -s youda_res/mitmproxy_newhouse.py
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
    collection = db[setting['mongo_235']['collection_newhouse']]
    # todo 新房成交处理数据入库
    try:
        data_list = json.loads(str(response.text))['data']['sets']['items']
    except Exception as e:
        info('序列化失败,数据格式不标准, e={}'.format(e))
        return
    for data in data_list:
        if not collection.find_one({'area': data['area'], 'plate': data['plate'],
                                    'module': data['module'], 'fullhousingname': data['fullhousingname'],
                                    'newdiskname': data['newdiskname'], 'roadlaneno': data['roadlaneno'],
                                    'unitprice': data['unitprice'], 'acreage': data['acreage'], 'usd': data['usd'],
                                    'housetype': data['housetype'], 'signingdate': data['signingdate'],
                                    'propertytype': data['propertytype'], 'address': data['address'],
                                    'resultprice': data['resultprice'], 'resultusd': data['resultusd'],
                                    'referenceprice': data['referenceprice'], 'referenceusd': data['referenceusd'],
                                    'houseproperty': data['houseproperty'], 'roomtype': data['roomtype'],
                                    'floor': data['floor']}):
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
    roadlaneno　　       地址
    unitprice　          均价
    acreage　　　　　　　面积
    usd　                总价
    housetype　　　　　　房屋类型
    signingdate　        签约日期
    propertytype　       小区类型
    address　            案例地址
    resultprice          合同单价
    resultusd            合同总价
    referenceprice       参考单价
    referenceusd         参考总价
    houseproperty        房屋性质
    roomtype             户型
    floor                当前层次
    """