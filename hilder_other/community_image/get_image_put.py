import requests
import pymongo
import pika
import json
from bson.objectid import ObjectId
from multiprocessing import Process
from retry import retry
import time


def get_collection_object(host, port, db_name, collection_name):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]
    return collection


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, ))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


m = get_collection_object('192.168.0.61', 27017, 'buildings', 'house_image_demo')
url = 'http://open.fangjia.com/files/upload'

token = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB'
data = {
    'token': token,
}

channel = connect_rabbit('192.168.0.235', 'image_stand')


def put_in_queue():
    coll = m.find_one({'_id': ObjectId('5a4c8d33c720b21b2025903e')})
    del coll['_id']
    channel.basic_publish(exchange='',
                          routing_key='image_stand_test',
                          body=json.dumps(coll),
                          )


# @retry(tries=3)
# def call_request(url,files,data,img):
#     try:
#         time.sleep(1)
#         reslut = requests.post(url=url, files=files, data=data)
#         code = reslut.json()['code']
#         if code is 200:
#             res_json = reslut.json()
#             link = res_json['result']['link']
#             img['link'] = link
#         else:
#             print(reslut.json())
#         return img
#     except Exception as e:
#         print('retry:',time.time())
#         raise
def callback(ch, method, properties, body):
    name = method.consumer_tag.split('.')[1]
    body = json.loads(body.decode())
    image_list = body['image_list']
    community = body['community']
    print(community)
    img_list = []
    try:
        for i in image_list:
            img = i['img']
            response = requests.get(img)
            if response.status_code is not 200:
                print(response.status_code)
                continue
            with open('D:/imagesss/{0}.png'.format(name), 'wb') as f:
                f.write(response.content)
            files = {'file': open('D:/imagesss/{0}.png'.format(name), 'rb')}
            reslut = requests.post(url=url, files=files, data=data)
            code = reslut.json()['code']
            if code is 200:
                res_json = reslut.json()
                link = res_json['result']['link']
                i['link'] = link
                img_list.append(i)
            else:
                print(1 / 0)
        m.update({'community': community}, {'$set': {'image_list': img_list}})
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(e)
        channel.basic_publish(exchange='',
                              routing_key='image_stand',
                              body=json.dumps(body),
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue='image_stand')
    channel.start_consuming()


if __name__ == '__main__':
    # Process(target=consume_queue).start()
    #   put_in_queue()
    for i in range(15):
        Process(target=consume_queue).start()
