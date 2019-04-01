from dateutil import parser
from lib.mongo import Mongo
import re
import json
import requests
import random
import yaml
from lib.log import LogHandler
from lib.rabbitmq import Rabbit

proxy = [{"https": "http://192.168.0.96:4234"},
         {"https": "http://192.168.0.93:4234"},
         {"https": "http://192.168.0.90:4234"},
         {"https": "http://192.168.0.94:4234"},
         {"https": "http://192.168.0.98:4234"},
         {"https": "http://192.168.0.99:4234"},
         {"https": "http://192.168.0.100:4234"},
         {"https": "http://192.168.0.101:4234"},
         {"https": "http://192.168.0.102:4234"},
         {"https": "http://192.168.0.103:4234"}, ]

m = Mongo('192.168.0.235')
connect = m.connect

setting = yaml.load(open('config.yaml'))

db_name = setting['CEIC']['mongo']['db']
State_indicators_name = setting['CEIC']['mongo']['State_indicators']
State_indicators_details_name = setting['CEIC']['mongo']['State_indicators_details']
log = LogHandler('ceic_detail')

r = Rabbit(setting['CEIC']['rabbit']['host'], setting['CEIC']['rabbit']['port'])


class Detail:
    def create_date(self, indexFrequency, start_year, start_mouth, end_year, ):
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

    def get_url(self):
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

            url_list = self.create_date(indexFrequency, start_year, start_mouth, end_year, )

            url = info['url']

            while True:
                try:
                    proxy_ = proxy[random.randint(0, 9)]
                    res = requests.get(url=url, proxies=proxy_)
                    if res.status_code == 200:
                        break
                except Exception as e:
                    print('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
                    # log.info('请求出错，url={}，proxy={}，'.format(url, proxy_), e)
            city_type = re.search('<img src="https://www.ceicdata.com/.*?/.*?/(.*?)/', res.content.decode(),
                                  re.S | re.M).group(1)
            for i in url_list:
                channel = r.get_channel()
                queue = setting['CEIC']['rabbit']['queue']
                print(r)
                channel.queue_declare(queue=queue)

                url = 'https://www.ceicdata.com/datapage/charts/' + city_type + '?type=column&' + i + '&width=1500&height=700'
                # print(url)
                body = {
                    'url': url,
                    'countryEnName': countryEnName,
                    'indexEnName': indexEnName
                }
                channel.basic_publish(exchange='',
                                      routing_key=queue,
                                      body=json.dumps(body))
                print('url放入队列成功{}'.format(body))
                channel.close()
                # log.info('url放入队列成功{}'.format(body))

