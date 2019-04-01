import requests
import pymongo
import pika
from multiprocessing import Process
import json
import yaml
from lib.log import LogHandler
import datetime


log = LogHandler('上海物业楼栋')

def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db_auth = client.admin
    db_auth.authenticate('goojia', 'goojia7102')
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, 5673))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


setting = yaml.load(open('config.yaml'))
sect_queue = setting['sh_wuye']['rabbit']['queue']['wuye_sect_id']
build_queue = setting['sh_wuye']['rabbit']['queue']['wuye_building_id']
wuye_coll = connect_mongodb(setting['sh_wuye']['mongo']['host'], setting['sh_wuye']['mongo']['port'],
                            setting['sh_wuye']['mongo']['db'], setting['sh_wuye']['mongo']['sect_coll'])
wuye_building = connect_mongodb(setting['sh_wuye']['mongo']['host'], setting['sh_wuye']['mongo']['port'],
                                setting['sh_wuye']['mongo']['db'], setting['sh_wuye']['mongo']['build_coll'])
channel = connect_rabbit(setting['sh_wuye']['rabbit']['host'], setting['sh_wuye']['rabbit']['queue']['wuye_sect_id'])

headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}


def callback(ch, method, properties, body):
    community_id = body.decode()
    url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getUnitListSDO.do'
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"sect_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n1\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n10000\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select\"\r\n\r\n\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_name\"\r\n\r\n15021630956\r\n--0xKhTmLbOuNdArY--".format(
        community_id)
    try:
        response = requests.post(url=url, headers=headers, data=payload, verify=False)
        data = response.json()
        message = data['message']
        for i in message:
            i['create_time'] = datetime.datetime.now()
            channel.queue_declare(queue=build_queue)
            channel.basic_publish(exchange='',
                                  routing_key=build_queue,
                                  body=json.dumps(i))
            log.info(json.dumps(i))
            wuye_building.insert_one(i)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error('请求错误，url="{}"'.format(url))
        channel.basic_publish(exchange='',
                              routing_key=sect_queue,
                              body=body,
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue=sect_queue)
    channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
    # for i in range(10):
    #     Process(target=consume_queue).start()
