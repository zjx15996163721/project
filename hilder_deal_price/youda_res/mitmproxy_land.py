from mitmproxy import ctx
from pymongo import MongoClient
import datetime
import json
import yaml
"""
启动方法
虚拟环境 mitmdump -s youda_res/mitmproxy_land.py
"""


def response(flow):

    response = flow.response

    info = ctx.log.info

    # info(str(response.status_code))

    # info(str(response.headers))

    # info(str(response.cookies))

    info(str(response.text))
    setting = yaml.load(open('res_config.yaml'))

    m = MongoClient(host=setting['mongo_235']['host'],
                    port=setting['mongo_235']['port'],
                    username=setting['mongo_235']['user_name'],
                    password=setting['mongo_235']['password'])
    db = m[setting['mongo_235']['db_name']]
    collection = db[setting['mongo_235']['collection_land']]
    # todo 土地成交处理数据入库
    try:
        data_list = json.loads(str(response.text))['data']['items']
    except Exception as e:
        info('序列化失败,数据格式不标准, e={}'.format(e))
        return
    for data in data_list:
        if not collection.find_one({'area': data['area'], 'plate': data['plate'],
                                    'module': data['module'], 'landname': data['landname'],
                                    'landuseplan': data['landuseplan'], 'landarea': data['landarea'],
                                    'buildingarea': data['buildingarea'], 'volumeratio': data['volumeratio'],
                                    'startprice': data['startprice'], 'usd': data['usd'],
                                    'premiumrate': data['premiumrate'], 'landunitprice': data['landunitprice'],
                                    'bargainfloorprice': data['bargainfloorprice'], 'unitprice': data['unitprice'],
                                    'developers': data['developers'], 'bargaindate': data['bargaindate'],
                                    'landaddress': data['landaddress'], 'landdescription': data['landdescription'],
                                    'floorprice': data['floorprice'], 'sellway': data['sellway'],
                                    'state': data['state']}):
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
    landname　           土地名称
    landuseplan      　　规划用途
    landarea　　         土地面积
    buildingarea         建筑面积
    volumeratio          容积率
    startprice           起拍价
    usd                  成交总价
    premiumrate          溢价率
    landunitprice        土地单价
    bargainfloorprice    成交楼盘价
    unitprice            单价
    developers           用地单位
    bargaindate          成交日期
    landaddress          地址
    landdescription      用途说明
    floorprice           起拍楼板价
    sellway              出让方式
    state                成交
    """