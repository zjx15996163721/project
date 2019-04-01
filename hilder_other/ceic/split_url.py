"""
从库里面取出列表页数据，拼接时间放入消费队列
"""
import pika
from dateutil import parser
from lib.mongo import Mongo
import re
import json
import requests
import random
import yaml
from lib.log import LogHandler
from lib.rabbitmq import Rabbit
import json

m = Mongo('192.168.0.235')
connect = m.connect

setting = yaml.load(open('config.yaml'))
db_name = setting['CEIC']['mongo']['db']

State_indicators_name = setting['CEIC']['mongo']['State_indicators']
State_indicators_details_name = setting['CEIC']['mongo']['State_indicators_details']
log = LogHandler('ceic_detail')


def create_date(indexFrequency, start_year, start_mouth, end_year, ):
    """

    :return: ['from=2016-1&to=2017-1', 'from=2016-1&to=2017-1', 'from=2016-1&to=2017-1', 'from=2016-1&to=2017-1',]
    """
    """
    根据开始时间分割年月日
    """
    if indexFrequency == '年':
        # print('年')
        s = [str(start_year) + '-' + str(start_mouth)]
        # print(start_year, end_year)
        while start_year < end_year:
            start_year = start_year + 11
            s.append(str(start_year) + '-' + str(start_mouth))
        # print(s)
    elif indexFrequency == '季':
        # print('季')
        s = [str(start_year) + '-' + str(start_mouth)]
        # print(start_year, end_year)
        while start_year < end_year:
            start_year = start_year + 2
            s.append(str(start_year) + '-' + str(start_mouth))
        # print(s)
    else:
        # print('月')
        s = [str(start_year) + '-' + '1']
        # print(start_year, end_year)
        while start_year < end_year:
            start_year = start_year + 1
            s.append(str(start_year) + '-' + '1')
        complete_url_list = []
        for i in range(0, len(s) - 1):
            complete_url_list.append('from=' + s[i] + '&' + 'to=' + s[i] + '2')
        # log.info('complete_url_list', complete_url_list)
        return complete_url_list
        # print(s)
    # from=2016-1&to=2017-1
    complete_url_list = []
    for i in range(0, len(s) - 1):
        complete_url_list.append('from=' + s[i] + '&' + 'to=' + s[i + 1])
    # log.info('complete_url_list', complete_url_list)
    return complete_url_list


class ProducerUrl:
    def __init__(self):
        self.rabbit_connection = Rabbit(setting['CEIC']['rabbit']['host'], setting['CEIC']['rabbit']['port'])

    def put_url_in_queue(self):
        # print(id(r))
        # return
        collection = connect[db_name][State_indicators_name]
        for info in collection.find():
            """
            info :
            {
                "_id" : ObjectId("5ad8389685699237a0c8ae90"),
                "indexUpdate" : "2018-03-28",
                "indexFrequency" : "季",
                "indexEnName" : "nominal-gdp",
                "indexEnd" : "2017-12",
                "url" : "https://www.ceicdata.com/zh-hans/indicator/united-states/nominal-gdp",
                "indexStart" : "1947-03",
                "indexName" : "名义国内生产总值",
                "indexCategory" : "国民经济核算",
                "indexUnit" : "百万美元",
                "countryName" : "美国",
                "countryEnName" : "united-states"
            }
            """

            countryEnName = info['countryEnName']
            # print(countryEnName)
            indexEnName = info['indexEnName']

            indexStart = info['indexStart']
            indexEnd = info['indexEnd']
            indexFrequency = info['indexFrequency']

            start_year = int(indexStart.split('-')[0])
            start_mouth = int(indexStart.split('-')[1])

            end_year = int(indexEnd.split('-')[0])
            end_mouth = int(indexEnd.split('-')[1])
            # print(start_year, start_mouth, end_year, end_mouth)

            url_list = create_date(indexFrequency, start_year, start_mouth, end_year, )

            url = info['url']

            data = {
                'url': url,
                'url_list': url_list,
                'countryEnName': countryEnName,
                'indexEnName': indexEnName
            }

            channel = self.rabbit_connection.connection.channel()

            channel.queue_declare(queue='ceic_url_to_be_split')
            channel.basic_publish(exchange='',
                                  routing_key='ceic_url_to_be_split',
                                  body=json.dumps(data))
            print('消息放入队列')
            channel.close()
        self.rabbit_connection.connection.close()


class ConsumerUrl:
    def __init__(self):
        self.proxy = [{"https": "http://192.168.0.96:4234"},
                      {"https": "http://192.168.0.93:4234"},
                      {"https": "http://192.168.0.90:4234"},
                      {"https": "http://192.168.0.94:4234"},
                      {"https": "http://192.168.0.98:4234"},
                      {"https": "http://192.168.0.99:4234"},
                      {"https": "http://192.168.0.100:4234"},
                      {"https": "http://192.168.0.101:4234"},
                      {"https": "http://192.168.0.102:4234"},
                      {"https": "http://192.168.0.103:4234"}, ]
        self.rabbit_connection = Rabbit(setting['CEIC']['rabbit']['host'], setting['CEIC']['rabbit']['port'])

    def start_consumer(self):
        channel = self.rabbit_connection.connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.queue_declare(queue='ceic_url_to_be_split')
        channel.basic_consume(self.callback,
                              queue='ceic_url_to_be_split',
                              no_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        result = json.loads(body.decode())
        url = result['url']
        url_list = result['url_list']
        countryEnName = result['countryEnName']
        indexEnName = result['indexEnName']

        while True:
            try:
                proxy_ = self.proxy[random.randint(0, 9)]
                res = requests.get(url=url, proxies=proxy_)
                if res.status_code == 200:
                    print('重新请求')
                    break
            except Exception as e:
                print('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
                # log.info('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
        city_type = re.search('<img src="https://www.ceicdata.com/.*?/.*?/(.*?)/', res.content.decode(),
                              re.S | re.M).group(1)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.190', port=5673))
        channel_ = connection.channel()
        for i in url_list:
            queue = setting['CEIC']['rabbit']['queue']

            url = 'https://www.ceicdata.com/datapage/charts/' + city_type + '?type=column&' + i + '&width=1500&height=700'
            # print(url)
            body = {
                'url': url,
                'countryEnName': countryEnName,
                'indexEnName': indexEnName
            }

            channel_.queue_declare(queue=queue)
            channel_.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=json.dumps(body))
            print('url放入队列成功{}'.format(body))
        channel_.close()
        connection.close()
