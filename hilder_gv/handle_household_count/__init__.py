from pymongo import MongoClient
import gevent
import re
import threading
from bson import ObjectId
# from lib.match_district import match
# from gevent import monkey
# monkey.patch_all()
# m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
# collection_delete_repeat = m['hilder_gv']['gv_merge_final']
# collection_delete_repeat.find_one_and_update()
TEST136client = MongoClient('192.168.0.38', 27007)
collection_seaweed = TEST136client.get_database("fangjia").seaweed

finish_building_date_count = 0
household_count_count = 0
estate_charge_count = 0
total_count = 0
for i in collection_seaweed.find({"visible": 0, "cat": "district", 'city': '合肥'}):
    total_count += 1
    if 'finish_building_date' in i:
        v = i['finish_building_date']
        print(v)
        if v == None or v == [] or v == "[]" or v == "" or v == 0 or v == False or v == '0.0':
            pass
        else:
            finish_building_date_count += 1

    if 'household_count' in i:
        v = i['household_count']
        print(v)
        if v == None or v == [] or v == "[]" or v == "" or v == 0 or v == False or v == '0.0':
            pass
        else:
            household_count_count += 1

    if 'estate_charge' in i:
        v = i['estate_charge']
        print(v)
        if v == None or v == [] or v == "[]" or v == "" or v == 0 or v == False or v == '0.0':
            pass
        else:
            estate_charge_count += 1



print('有效的竣工时间{}'.format(finish_building_date_count))
print('总量{}'.format(total_count))
print(finish_building_date_count/total_count)


print('有效的户数{}'.format(household_count_count))
print('总量{}'.format(total_count))
print(household_count_count/total_count)

print('有效的物业费{}'.format(estate_charge_count))
print('总量{}'.format(total_count))
print(estate_charge_count/total_count)