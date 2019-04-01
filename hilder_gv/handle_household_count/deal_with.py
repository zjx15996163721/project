"""
合法性判断
"""
import time
from pymongo import MongoClient
import gevent
from lib.match_district import match
from gevent import monkey
monkey.patch_all()
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_delete_repeat = m['hilder_gv']['gv_merge_final']
collection_merge = m['hilder_gv']['gv_merge']


def start(i):
    household_count_list = []
    complete_time_list = []
    estate_charge_list = []

    for _id in i['_id_list']:
        data = collection_merge.find_one({'_id': _id})

        if data['household_count'] and data['household_count'] is not None and 50 <= int(data['household_count']) <= 100000:
                household_count_list.append(str(data['household_count']))

        if data['complete_time'] and data['complete_time'] is not None:
            complete_time_list.append(str(data['complete_time']))

        if data['estate_charge'] and data['estate_charge'] is not None:
            if type(data['estate_charge']) == str and '至' in data['estate_charge']:
                new_estate_charge = data['estate_charge'].split('至')[0]
                new_estate_charge_second = data['estate_charge'].split('至')[1]
                if 0.2 <= float(new_estate_charge) <= 3.5:
                    estate_charge_list.append(str(data['estate_charge']))

                elif 0.2 <= float(new_estate_charge_second) <= 3.5:
                    estate_charge_list.append(str(data['estate_charge']))
                else:
                    print('无效的物业费{}'.format(str(data['estate_charge'])))

            elif 0.2 <= float(data['estate_charge']) <= 3.5:
                estate_charge_list.append(str(data['estate_charge']))

            else:
                print('无效的物业费{}'.format(str(data['estate_charge'])))

    collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'household_count_list': household_count_list,
                                                                              'complete_time_list': complete_time_list,
                                                                              'estate_charge_list': estate_charge_list}})
    print('更新户数{}，竣工时间{}，物业费{}'.format(household_count_list, complete_time_list, estate_charge_list))
    household_count_list.clear()
    complete_time_list.clear()
    estate_charge_list.clear()


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_delete_repeat.find(no_cursor_timeout=True):
        count += 1
        print(count)
        if len(data_list) == 50:
            tasks = [gevent.spawn(start, data) for data in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            data_list.append(i)
    if len(data_list) > 0:
        tasks = [gevent.spawn(start, data) for data in data_list]
        gevent.joinall(tasks)
        data_list.clear()


