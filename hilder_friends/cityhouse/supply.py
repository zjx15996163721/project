"""
城市房产,列表页请求失败部分补充,
"""
import math
import re
import json
import pika
import requests
import yaml
from cityhouse.citylist import items
from lib.proxy_iterator import Proxies
from lib.log import LogHandler

log = LogHandler(__name__)
setting = yaml.load(open('config.yaml'))
p = Proxies()

host = setting['cityhouse']['rabbit']['host']
port = setting['cityhouse']['rabbit']['port']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36'
}
proxy = next(p)


def supply():
    with open('./log/cityhouse.producer.log', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if re.search('ERROR 城市=(.*?),', line):
                error_city = re.search('ERROR 城市=(.*?),', line).group(1)
                for province in items['items']:
                    city_list = province['citys']
                    for city in city_list:
                        city_code = city['cityCode']
                        city_name = city['cityName']
                        if error_city == city_name:
                            url = 'http://api.cityhouse.cn/csfc/v2/ha/list?percount=10&proptype=11&page=1&apiKey=4LiEDwxaRaAYTA3GBfs70L&ver=2&city=' \
                                  + city_code
                            try:
                                res = requests.get(url, headers=headers, proxies=proxy)
                                total = res.json()['totalSize']
                                print(city_name, total)
                            except:
                                log.error('城市={},请求失败'.format(city_name))
                                continue
                            if total == 0:
                                log.info('当前城市={},暂无数据'.format(city_name))
                                continue
                            page = math.ceil(total / 100)
                            for i in range(1, int(page) + 1):
                                all_url = 'http://api.cityhouse.cn/csfc/v2/ha/list?percount=100&proptype=11&page=' + str(
                                    i) + '&apiKey=4LiEDwxaRaAYTA3GBfs70L&ver=2&city=' \
                                          + city_code
                                try:
                                    t_res = requests.get(all_url, headers=headers, proxies=proxy, timeout=20)
                                    connection.process_data_events()
                                    put_queue(t_res, city_name, city_code)
                                except Exception as e:
                                    log.error('{}请求失败，error={}'.format(all_url, e))
                                    continue
            elif re.search('ERROR (http://.*?)请求失败', line):
                url = re.search('ERROR (http://.*?)请求失败', line).group(1)
                e_city = re.search('city=(.*?)请求失败', line).group(1)
                for province in items['items']:
                    city_list = province['citys']
                    for city in city_list:
                        city_code = city['cityCode']
                        city_name = city['cityName']
                        if city_code == e_city:
                            try:
                                t_res = requests.get(url, headers=headers, proxies=proxy, timeout=20)
                                connection.process_data_events()
                                put_queue(t_res, city_name, city_code)
                            except Exception as e:
                                log.error('{}请求失败，error={}'.format(url, e))


def put_queue(res, city_name, city_code):
    """
    消息队列名称为cityhouse
    :param res:
    :param city_name:
    :param city_code:
    :return:
    """
    city_message = []
    channel = connection.channel()
    for comm in res.json()['items']:
        comm_id = comm['id']
        city_message.append((city_name, comm_id, city_code))
    channel.queue_declare(queue='cityhouse')
    channel.basic_publish(exchange='',
                          routing_key='cityhouse',
                          body=json.dumps(city_message))
    print('{}已放入队列'.format(city_name))
    city_message.clear()
