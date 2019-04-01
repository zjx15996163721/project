import pymongo

from community_image.bloomfilter_redis import BloomFilter


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


coll_real = get_pymongo_config('buildings', 'community_image_real', '192.168.0.61', 27017)
coll = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
community_list = coll.find()
count = 0
bf = BloomFilter()
for i in community_list:
    community = i['community']
    if not bf.isContains(community):
        bf.insert(community)
        data = {
            'image_list':i['image_list'],
            'city':i['city'],
            'job_id':i['job_id'],
            'community':i['community'],
            'area':i['area'],
        }
        print(community)
        # coll_real.insert(data)
        count += 1
        print(count)
    else:
        continue
