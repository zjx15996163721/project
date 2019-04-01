import pymongo
import pika
import requests
import json
import yaml
from multiprocessing import Process
from lib.log import LogHandler
import datetime

log = LogHandler('上海物业房号')


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


headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}
url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getHouListSDO.do'

setting = yaml.load(open('config.yaml'))

wuye_house = connect_mongodb(setting['sh_wuye']['mongo']['host'], setting['sh_wuye']['mongo']['port'],
                             setting['sh_wuye']['mongo']['db'], setting['sh_wuye']['mongo']['house_coll'])

build_queue = setting['sh_wuye']['rabbit']['queue']['wuye_building_id']
channel = connect_rabbit(setting['sh_wuye']['rabbit']['host'], build_queue)


def callback(ch, method, properties, body):
    message = body.decode()
    data = json.loads(message)
    unit_no = data['unit_no']
    unit_id = data['unit_id']
    sect_id = data['sect_id']
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n1\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"unit_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select\"\r\n\r\n\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n1000\r\n--0xKhTmLbOuNdArY--".format(
        unit_id)
    try:
        response = requests.post(url=url, headers=headers, data=payload, verify=False, )
        data = response.json()
        message = data['message']
        for i in message:
            hou_addr = i['hou_addr']
            st_name_frst = i['st_name_frst']
            hou_no = i['hou_no']
            hou_id = i['hou_id']
            data = {
                'unit_id': unit_id,
                'sect_id': sect_id,
                'unit_no': unit_no,
                'hou_addr': hou_addr,
                'st_name_frst': st_name_frst,
                'hou_no': hou_no,
                'hou_id': hou_id,
                'create_time':datetime.datetime.now()
            }
            log.info(json.dumps(data))
            wuye_house.insert_one(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error('请求错误，url="{}"'.format(url))
        channel.basic_publish(exchange='',
                              routing_key=build_queue,
                              body=body,
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue=build_queue)
    channel.start_consuming()


if __name__ == '__main__':
    # for i in range(60):
    #     Process(target=consume_queue).start()
    consume_queue()
