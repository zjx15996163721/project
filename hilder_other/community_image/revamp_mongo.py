import pymongo


def get_collection_object(host, port, db_name, collection_name):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]
    return collection


m = get_collection_object('192.168.0.61', 27017, 'buildings', 'house_image_demo2')
for i in m.find():
    _id = i['_id']
    print(_id)
    image_list = i['image_list']
    img_list = []
    for i in image_list:
        if 'rommsize' in i:
            i['roomsize'] = i['rommsize']
            i['img'] = i['img_url']
            del i['rommsize']
            del i['img_url']
            img_list.append(i)
    if not img_list:
        continue
    m.update({'_id': _id}, {'$set': {"image_list": img_list}}, False, True)
