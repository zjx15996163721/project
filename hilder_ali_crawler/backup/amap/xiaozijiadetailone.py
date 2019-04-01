# -*- coding: utf-8 -*-
# @Time    : 2018/7/30 14:49
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : xiaozijiadetailone.py
# @Software: PyCharm

import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.195', port=5673))
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_detail')


def callback(ch, method, properties, body):
    new_body = json.loads(body.decode())
    new_list = []
    for i in range(0, len(new_body), 100):
        new_list.append(new_body[i:i+100])

    for j in new_list:
        channel.queue_declare(queue='xiaozijia_detail_1')
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_detail_1',
                              body=json.dumps(j)
                              )
        print('放入新队列 {}'.format(j))


def consume_start():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='xiaozijia_detail', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    consume_start()
