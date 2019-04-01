from pymongo import MongoClient
from deal_price_info import Comm
import re

m = MongoClient(host='192.168.0.43', port=27017)
collection_new = m['business']['new_deal_price']
collection = m['business']['esf_deal_price']

number_dict = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
}


def check_room(number):
    return number_dict[number]


class Youda:
    def __init__(self):
        self.new_source = '新友达'
        self.source = '友达'

    def new_deal_price(self):
        for i in collection_new.find(no_cursor_timeout=True):
            print(collection_new.database.client.address[0])
            if 'fj_flag' in i:
                if i['fj_flag'] == 1:
                    deal_price = Comm(self.new_source)
                    deal_price.city = i['fj_city']
                    deal_price.region = i['fj_region']
                    deal_price.district_name = i['fj_name']
                    deal_price.avg_price = float(i["CJDJ"])
                    # deal_price.total_price = float(i["CJJE"]) * 10000
                    deal_price.trade_date = i['CJRQ']
                    deal_price.area = float(i['JZMJ'])
                    deal_price.room_num = i['SH']

                    deal_price.total_price = float(i['JZMJ']) * float(i["CJDJ"])
                    try:
                        room = re.search('(.)室', i['FX'], re.S | re.M).group(1)
                        deal_price.room = check_room(room)
                    except Exception as e:
                        print('找不到室,FX={}, e={}'.format(i['FX'], e))
                    try:
                        hall = re.search('(.)厅', i['FX'], re.S | re.M).group(1)
                        deal_price.hall = check_room(hall)
                    except Exception as e:
                        print('找不到厅,FX={}, e={}'.format(i['FX'], e))
                    is_success = deal_price.insert_db()
                    # if is_success:
                    #     print('修改done')
                    #     collection_new.update_one({'_id': i['_id']}, {'$set': {'done': 1}})

    def deal_price(self):
        for data in collection.find(no_cursor_timeout=True):
            if 'fj_flag' in data:
                if data['fj_flag'] == 1:
                    second_price = Comm(self.source)
                    second_price.city = data['fj_city']
                    second_price.direction = data['CJ_CX']
                    second_price.avg_price = float(data['CJ_CJDJ'])
                    second_price.area = float(data['CJ_JZMJ'])
                    second_price.trade_date = data['CJ_CJRQ']

                    second_price.total_price = float(data['CJ_CJDJ']) * float(data['CJ_JZMJ'])

                    second_price.district_name = data['fj_name']
                    if 'CJ_ZH' in data:
                        second_price.house_num = data['CJ_ZH']
                    if 'CJ_SHBW' in data:
                        second_price.room_num = data['CJ_SHBW']
                    try:
                        second_price.floor = int(data['CJ_CS'])
                    except Exception as e:
                        print('楼层error', e)
                    second_price.region = data['fj_region']
                    is_success = second_price.insert_db()
                    # if is_success:
                    #     collection.update_one({'_id': data['_id']}, {'$set': {'done': 1}})
