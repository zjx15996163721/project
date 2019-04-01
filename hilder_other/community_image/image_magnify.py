import pymongo
from multiprocessing import Process


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


coll_put = get_pymongo_config('buildings', 'community_image_det1', '192.168.0.61', 27017)
# 安居客
# img_list = coll_put.find({'job_id':'5a30bbd1e4b0e452ecb4c4d6'})
# 链家
# img_list = coll_put.find({'job_id': '5a30bbd8e4b0e452ecb4c4d8'})
# #新浪
img_list = coll_put.find({'job_id':'5a30bbe0e4b0e452ecb4c4da'})
count = 0


def image_ma(rule):
    for i in img_list:
        global count
        count += 1
        print(count)
        id1 = i['_id']
        img = i['img']
        i['img'] = img.replace(rule, '748x578')
        print(i)
        coll_put.update({'_id': id1}, {'$set': {'img': i['img']}})


if __name__ == '__main__':
    # 链家
    # Process(target=image_ma, args=('280x',)).start()
    # 新浪
    Process(target=image_ma, args=('358X269',)).start()
    # #安居客
    # Process(target=image_ma,args=('240x180n',)).start()
