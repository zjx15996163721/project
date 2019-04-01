import os
import requests
import hashlib
import pymongo
from retry import retry

token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
data = {
    'token': token,
}
url = 'http://open.fangjia.com/files/upload'


# def eachFile(filepath):
#     pathDir = os.listdir(filepath)
#     for allDir in pathDir:
#         print(allDir)
#         child = os.path.join('%s\%s' % (filepath, allDir))
#         files = {'file': open(child, 'rb')}
#         reslut = requests.post(url=url, files=files, data=data)
#         print(reslut.text)
#         break


def get_collection_object(host, port, db_name, collection_name):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]
    return collection


m = get_collection_object('192.168.0.235', 27017, 'image_test', 'image_test')


@retry(tries=3)
def retry_(result):
    try:
        print(1 / 0)
        link = result.json()['result']['link']
        return link
    except Exception as e:
        print('重试一次-----------------------------------')
        raise


def start():
    for i in m.find():
        image_list = i['image_list']
        _id = i['_id']
        img_list = []
        for i in image_list:
            img = i['img']
            m1 = hashlib.md5()
            m1.update(img.encode('utf-8'))
            md5_url = m1.hexdigest()
            file_path = 'D:\\imagesss\\' + md5_url + '.png'
            try:
                files = {'file': open(file_path, 'rb')}
                result = requests.post(url=url, files=files, data=data)
                link = retry_(result)

                i['link'] = link
                img_list.append(i)

            except Exception as e:
                print('没有图片')

        print(img_list)
        m.update({'_id': _id}, {'$set': {'image_list': img_list}})


if __name__ == '__main__':
    start()
