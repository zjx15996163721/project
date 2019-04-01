from pymongo import MongoClient
from bson import ObjectId
import gevent
# from gevent import monkey
# monkey.patch_all()
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_delete_repeat = m['hilder_gv']['gv_merge_delete_repeat']
collection_delete_repeat.update_one()
# n = MongoClient(host='192.168.0.136', port=27017)
# collection_seaweed = n['fangjia']['seaweed']
TEST136client = MongoClient('192.168.0.38', 27007)
collection_seaweed = TEST136client.get_database("fangjia").seaweed


def start(i):
    # fj_city = i['fj_city']
    # fj_region = i['fj_region']
    # fj_name = i['fj_name']
    fj_id = i['fj_id']
    household_count = i['household_count']
    print(household_count)

    complete_time = i['complete_time']
    print(complete_time)

    estate_charge = i['estate_charge']
    print(estate_charge)

    data = collection_seaweed.find_one({'_id': ObjectId(fj_id)})
    print(data)

    new_household_count = data.get('household_count', None)    # int
    print(new_household_count)

    finish_building_date = data.get('finish_building_date', None)  # str '2018-10-10'
    print(finish_building_date)

    new_estate_charge = data.get('estate_charge', None)          # str '0.8'
    print(new_estate_charge)

    if new_household_count is None:
        if household_count is not None:
            collection_seaweed.update_one({'_id': ObjectId(fj_id)}, {'$set': {'household_count': int(household_count)}})
            print('更新户数{}'.format(household_count))
    elif new_household_count is not None:
        try:
            if int(new_household_count) < int(household_count):
                collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                       {'$set': {'household_count': int(household_count)}})
                print('更新户数{}'.format(household_count))
        except Exception as e:
            print(e)

    if finish_building_date is None:
        if complete_time is not None:
            collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                   {'$set': {'finish_building_date': str(complete_time)}})
            print('更新竣工时间{}'.format(complete_time))
    elif finish_building_date is not None:
        if finish_building_date == '':
            collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                   {'$set': {'finish_building_date': str(complete_time)}})
            print('更新竣工时间{}'.format(complete_time))

    if new_estate_charge is None:
        if estate_charge is not None:
            collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                   {'$set': {'estate_charge': str(estate_charge)}})
            print('更新物业费{}'.format(estate_charge))
    elif new_estate_charge is not None:
        try:
            if new_estate_charge == '' and estate_charge is not None:
                collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                       {'$set': {'estate_charge': str(estate_charge)}})
                print('更新物业费{}'.format(estate_charge))
            elif estate_charge is not None and float(new_estate_charge) < float(estate_charge):
                collection_seaweed.update_one({'_id': ObjectId(fj_id)},
                                                       {'$set': {'estate_charge': str(estate_charge)}})
                print('更新物业费{}'.format(estate_charge))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    count = 0
    data_list = []
    for i in collection_delete_repeat.find({'fj_flag': 1}, no_cursor_timeout=True):
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

