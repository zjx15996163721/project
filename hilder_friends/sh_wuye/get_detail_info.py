import requests
import pymongo
import pika
from multiprocessing import Process
import yaml
import json
from lib.log import LogHandler
import datetime

log = LogHandler('上海物业小区详情页')

headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}


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
# 详情页 接口
url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getSectSDO.do'
wuye_detail = connect_mongodb(setting['sh_wuye']['mongo']['host'], setting['sh_wuye']['mongo']['port'],
                              setting['sh_wuye']['mongo']['db'], setting['sh_wuye']['mongo']['detail_coll'])
sect_id_coll = connect_mongodb(setting['sh_wuye']['mongo']['host'], setting['sh_wuye']['mongo']['port'],
                               setting['sh_wuye']['mongo']['db'], setting['sh_wuye']['mongo']['sect_coll'])
detail_queue = setting['sh_wuye']['rabbit']['queue']['wuye_sect_id_detail']
channel = connect_rabbit(setting['sh_wuye']['rabbit']['host'], detail_queue)


def callback(ch, method, properties, body):
    community_id = body.decode()
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"sect_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_id\"\r\n\r\n1801171076359845\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_name\"\r\n\r\n15021630956\r\n--0xKhTmLbOuNdArY--".format(
        community_id)
    try:
        response = requests.post(url=url, headers=headers, data=payload, verify=False)
        data = response.json()
        message = data['message']
        st_name_frst = message[0][0]['st_name_frst']
        st_addr_frst = message[0][0]['st_addr_frst']
        st_cnst_area = message[0][0]['st_cnst_area']
        sect_finish_date = message[0][0]['sect_finish_date']
        csp_name = message[0][0]['csp_name']
        sect_id = message[0][0]['sect_id']
        st_csp_servcie_type = message[0][0]['st_csp_servcie_type']
        save_date = {
            'st_name_frst': st_name_frst,
            'st_addr_frst': st_addr_frst,
            'st_cnst_area': st_cnst_area,
            'sect_finish_date': sect_finish_date,
            'csp_name': csp_name,
            'sect_id': sect_id,
            'st_csp_servcie_type': st_csp_servcie_type,
            'create_time':datetime.datetime.now()
        }
        log.info(json.dumps(save_date))
        wuye_detail.insert_one(save_date)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error('请求错误，url="{}"'.format(url))
        channel.basic_publish(exchange='',
                              routing_key=detail_queue,
                              body=body,
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue=detail_queue)
    channel.start_consuming()


if __name__ == '__main__':
    # for i in range(10):
    #     Process(target=consume_queue).start()
    consume_queue()
