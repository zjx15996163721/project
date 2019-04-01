from pymongo import MongoClient
import gevent
import threading
from lib.match_district import match
# from gevent import monkey
# monkey.patch_all()
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_delete_repeat = m['hilder_gv']['gv_merge_final']


def start(i):
    household_count_list = i['household_count_list']
    complete_time_list = i['complete_time_list']
    estate_charge_list = i['estate_charge_list']
    if len(household_count_list) > 0:
        new_household_count_list = []
        for household in household_count_list:
            new_household_count_list.append(int(household))
        household_count = max(new_household_count_list)
        collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'household_count': household_count}})
        print('更新户数{}'.format(household_count))
    else:
        collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'household_count': None}})
        print('户数为None')

    if len(complete_time_list) > 0:
        new_complete_time_list = []
        try:
            for complete in complete_time_list:
                new_complete_time_list.append(int(complete))
            complete_time = max(new_complete_time_list)
            collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'complete_time': complete_time}})
            print('更新建造年代{}'.format(complete_time))
        except Exception as e:
            print(e)
    else:
        collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'complete_time': None}})
        print('建造年代为None')

    if len(estate_charge_list) > 0:
        new_estate_charge_list = []
        for estate_charge in estate_charge_list:
            if '至' in estate_charge:
                if 0.2 <= float(estate_charge.split('至')[0]) <= 3.5:
                    new_estate_charge_list.append(float(estate_charge.split('至')[0]))
                if 0.2 <= float(estate_charge.split('至')[1]) <= 3.5:
                    new_estate_charge_list.append(float(estate_charge.split('至')[1]))

            else:
                new_estate_charge_list.append(float(estate_charge))

        new_estate_charge = max(new_estate_charge_list)
        collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'estate_charge': new_estate_charge}})
        print('更新物业费{}'.format(new_estate_charge))
    else:
        collection_delete_repeat.find_one_and_update({'_id': i['_id']}, {'$set': {'estate_charge': None}})
        print('物业费为None')


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_delete_repeat.find(no_cursor_timeout=True):
        count += 1
        print(count)
        if len(data_list) == 100:
            tasks = [gevent.spawn(start, data) for data in data_list]
            gevent.joinall(tasks)
            data_list.clear()
        else:
            data_list.append(i)
    if len(data_list) > 0:
        tasks = [gevent.spawn(start, data) for data in data_list]
        gevent.joinall(tasks)
        data_list.clear()

