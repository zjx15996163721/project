"""
去重

"""

from pymongo import MongoClient
import redis
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_merge = m['hilder_gv']['gv_merge']
collection_delete_repeat = m['hilder_gv']['gv_merge_final']

r = redis.Redis(host='localhost', port='6379')


def run():
    count = 0
    for i in collection_merge.find(no_cursor_timeout=True):
        count += 1
        print(count)
        _id = i['_id']
        try:
            city = i['city']
            region = i['region']
            district_name = i['district_name']
            city_region_district_name = city + region + district_name
        except:
            continue
        flag = r.sadd('gv_new', city_region_district_name)
        if flag == 1:
            # 不重复的数据
            _id_list = []
            _id_list.append(_id)
            data = {
                'city': city,
                'region': region,
                'district_name': district_name,
                '_id_list': _id_list
            }
            collection_delete_repeat.insert_one(data)
            print('插入一条数据{}'.format(data))
        elif flag == 0:
            # 重复的数据
            data = collection_delete_repeat.find_one({'city': city, 'region': region, 'district_name': district_name})
            if data:
                _id_list = data['_id_list']
                _id_list.append(_id)
                collection_delete_repeat.find_one_and_update({'_id': data['_id']},
                                                             {'$set': {'_id_list': _id_list}})
                print('更新_id_list={}'.format(_id_list))


if __name__ == '__main__':
    run()




