# -*- coding: utf-8 -*-
# @Time    : 2018/7/24 10:42
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : qiancheng_producer.py
# @Software: PyCharm

import pika
import requests
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',port=5673))
channel = connection.channel()
channel.queue_declare(queue='51job', durable=True)


class Jobs(object):
    def __init__(self):
        self.headers = {
            'Host': 'jobs.51job.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }

    def get_all_links(self):
        url_list = []
        for i in range(0, 9999999):
            url = 'https://jobs.51job.com/all/co' + str(i) + '.html'
            url_list.append(url)
            if len(url_list) == 72:
                print('将72条url放入队列中')
                channel.basic_publish(exchange='',
                                      routing_key='51job',
                                      body=json.dumps(url_list),
                                      # properties=pika.BasicProperties(delivery_mode=2,) #设置消息持久化
                                      )
                url_list.clear()
            # print('[生产者] Send message {}'.format(url))


# if __name__ == '__main__':
#     job = Jobs()
#     job.get_all_links()






