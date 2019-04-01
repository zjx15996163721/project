import json
import re
from lib.rabbitmq import Rabbit
import requests
from dateutil import parser
from lib.log import LogHandler
from lib.mongo import Mongo
import yaml

setting = yaml.load(open('config.yaml'))

# mongodb
m = Mongo('192.168.0.235')
connect = m.connect

db_name = setting['CEIC']['mongo']['db']
State_indicators_name = setting['CEIC']['mongo']['State_indicators']
State_indicators_details_name = setting['CEIC']['mongo']['State_indicators_details']
# rabbit
r = Rabbit(setting['CEIC']['rabbit']['host'], setting['CEIC']['rabbit']['port'])
channel = r.get_channel()
queue = setting['CEIC']['rabbit']['queue']
channel.queue_declare(queue=queue)
log = LogHandler('ceic_detail')


class Consumer(object):
    def callback(self, ch, method, properties, body):
        ip = method.consumer_tag
        body = json.loads(body.decode())
        url = body['url']
        countryEnName = body['countryEnName']
        indexEnName = body['indexEnName']
        while True:
            proxy_ = {'https': ip}
            try:
                res = requests.get(url=url, proxies=proxy_)
                if res.status_code == 200:
                    break
                if res.status_code == 404:
                    print('404')
                    return
            except Exception as e:
                print('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
                # log.info('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
        self.parse_detail(res.content.decode(), url, countryEnName, indexEnName)
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def parse_detail(self, html, url, countryEnName, indexEnName):
        data_info_list = re.search('<g class="highcharts-axis-labels highcharts-xaxis-labels ">(.*?)</g>', html,
                                   re.S | re.M).group(1)
        date_list = []
        for i in re.findall('<tspan>(.*?)</tspan>', data_info_list, re.S | re.M):
            date_list.append(i)

        num_list = []
        num_info_list = re.findall('<g class="highcharts-label highcharts-data-label(.*?)</g>', html, re.S | re.M)
        for k in num_info_list:
            value_ = re.search('<tspan .*?>(.*?)</tspan>', k, re.S | re.M).group(1)
            num_list.append(value_)

        if len(date_list) != len(num_list):
            # log.error('页面的数据和月份对应不上date_list={},num_list={}, url={},'.format(len(date_list), len(num_list), url))
            print('页面的数据和月份对应不上date_list={},num_list={}, url={},'.format(len(date_list), len(num_list), url))
            return
        # if len(date_list) or len(num_list) == 0:
        #     log.error('date_list=0,num_list=0, url={},'.format(url))
        #     return

        for j in range(0, len(date_list)):
            try:
                num = re.search('\d+', date_list[j], re.S | re.M).group(0)
                list_time = date_list[j].split('\'')

                """
                判断是19世纪还是20世纪
                """
                if int(num) > 20:
                    date_list[j] = list_time[0] + '19' + list_time[1]
                else:
                    date_list[j] = list_time[0] + '20' + list_time[1]
                # collection = connect['test']['State_indicators_details']
                collection = connect[db_name][State_indicators_details_name]
                data = {
                    'countryEnName': countryEnName,
                    'indexEnName': indexEnName,
                    'Date': parser.parse(date_list[j]).strftime('%Y-%m'),
                    'Value': num_list[j],
                }
                collection.update_one({'countryEnName': countryEnName, 'indexEnName': indexEnName,
                                       'Date': parser.parse(date_list[j]).strftime('%Y-%m')}, {'$set': data}, True)
                # log.info('{}城市详情入库成功,indexEnName={}'.format(countryEnName, indexEnName))
                print('{}城市详情入库成功,indexEnName={}'.format(countryEnName, indexEnName))
            except Exception as e:
                print(e)
                # log.error(e)

    def consume_start(self, ip):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue=queue, consumer_tag=ip)
        channel.start_consuming()
