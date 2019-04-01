"""
poi 详情 非官方详情
"""
import requests
import pymongo
import time


def get_poi(poi_coll, detail_coll, count_):
    for i in poi_coll.find():
        count_ += 1
        print(count_)

        poi_id = i['id']
        url = 'http://ditu.amap.com/detail/get/detail?id=' + poi_id
        result = requests.get(url).json()
        print(result)
        if result['status'] is '1':
            try:
                detail_coll.insert({'_id': poi_id,
                                    'data': result['data']})
            except pymongo.errors.DuplicateKeyError as e:
                # 插入的key相同
                print(e)
                continue
        elif result['status'] is '6':
            print('too fast')
            time.sleep(10)
        else:
            print('status is not 1: ', result)
            break


if __name__ == '__main__':
    client = pymongo.MongoClient('192.168.0.235', 27017)
    db = client['amap']
    poi = db.get_collection('poi_new')
    detail = db.get_collection('poi_detail')
    count = 0
    get_poi(poi, detail, count)
