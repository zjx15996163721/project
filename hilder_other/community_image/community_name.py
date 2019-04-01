import requests
import pymongo
import json


def get_pymongo_config(db_name, collection, ip, port):
    """
    :param db_name: 数据库名称
    :param collection: 表名称
    :return: mongodb collection
    """
    client = pymongo.MongoClient(ip, port)
    db = client[db_name]
    coll = db.get_collection(collection)
    return coll


token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
url = 'http://open.fangjia.com/address/match'
coll_put = get_pymongo_config('buildings', 'community_image_real', '192.168.0.61', 27017)
count = 0
for i in coll_put.find():
    city = i['city']
    suggestDistrict = i['area']
    address = i['community']
    url_all = url + '?city=' + city + '&token=' + token + '&suggestDistrict=' + suggestDistrict + '&address=' + address
    print(url_all)
    response = requests.get(url_all)
    response_json = json.loads(response.text)
    if response_json['code'] == 200:
        if response_json['result']['credit'] > 0:
            count += 1
        else:
            print('credits 不大于零')
            continue
    else:
        print('响应值不是200')
        continue
    print(count)
