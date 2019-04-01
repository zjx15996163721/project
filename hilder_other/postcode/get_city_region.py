# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 15:18
# @Author  : zjx
# @Email   : zhangjinxiao@fangjia.com
# @File    : get_city_region.py
# @Software: PyCharm
import requests
from lxml import etree
from pymongo import MongoClient
import urllib.parse
import re
from bs4 import BeautifulSoup
import pika
import json
import yaml

s = yaml.load(open('config_postcode.yaml'))
m = MongoClient(host=s['mongo']['host'], port=s['mongo']['port'], username=s['mongo']['user_name'], password=s['mongo']['password'])
db = m['postcode']
postcode_city_collection = db['postcode_all_city_new']
postcode_region_collection = db['postcode_all_region_new']

mongo = MongoClient(host=s['mongo198']['host'], port=s['mongo198']['port'])
db = mongo['fangjia']
server_area = db['server_area']
region_block = db['region_block']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=s['rabbit']['host'], port=s['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='postcode')


class GetCity(object):
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        self.proxies = proxies

    def get_province_city(self):
        for province_city in server_area.find(no_cursor_timeout=True):
            if 'province' in province_city:
                province = province_city['province']
                city = province_city['display']
                self.get_postcode(province, city)
            else:
                print('库中没有省份')

    def get_postcode(self, province, city):
        url = 'http://opendata.baidu.com/post/s?wd={}+{}&p=mini&rn=20'.format(urllib.parse.quote(province.encode('gbk')), urllib.parse.quote(city.encode('gbk')))
        print(url)
        province_name = province
        city_name = city
        r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        r_text = r.content.decode('gbk')
        soup = BeautifulSoup(r_text, 'lxml')
        info = soup.select('.table-list > tr > td')
        for i in range(0, len(info), 2):
            region_postcode = info[i].text
            region_name = info[i + 1].text
            data = {
                'province_name': province_name,
                'city_name': city_name,
                'region_postcode': region_postcode,
                'region_name': region_name
            }
            if postcode_city_collection.find_one({'province_name': province_name, 'city_name': city_name, 'region_postcode': region_postcode, 'region_name': region_name}) is None:
                postcode_city_collection.insert_one(data)
                print('插入一条数据 {}'.format(data))
            else:
                print('已经存在库中')
            # tree = etree.HTML(r_text)
            # city_postcode_a = tree.xpath("//article[@class='list-data']/ul[1]/li/a")[0]
            # info = city_postcode_a.xpath('string(.)')
            # city_postcode = re.search('(\d+)', info).group(1)
            # postcode_city_collection.update({'province_name': province_name, 'city_name': city_name, 'region_postcode': region_postcode, 'region_name': region_name}, {'$set': {'city_postcode': city_postcode}})
            # print('插入城市邮编')
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            r_text = r.content.decode('gbk')
            tree = etree.HTML(r_text)
            count_info = tree.xpath("//article[@class='mis-pager']/div/span/text()")[0]
            count = re.search('(\d+)', count_info).group(1)
            print(int(int(count) / 20))
            for i in range(1, int(int(count) / 20) + 1):
                self.get_next_page(province, city, i)
                print('抓取下一页')
        except Exception as e:
            print('没有翻页,只有一页')

    def get_next_page(self, province, city, i):
        url = 'http://opendata.baidu.com/post/s?p=mini&wd={}%20{}&pn={}&rn=20'.format(urllib.parse.quote(province.encode('gbk')), urllib.parse.quote(city.encode('gbk')), 20 * i)
        print(url)
        r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        r_text = r.content.decode('gbk')
        if '抱歉' not in r_text:
            province_name = province
            city_name = city
            soup = BeautifulSoup(r_text, 'lxml')
            info = soup.select('.table-list > tr > td')
            for i in range(0, len(info), 2):
                region_postcode = info[i].text
                region_name = info[i+1].text
                data = {
                    'province_name': province_name,
                    'city_name': city_name,
                    'region_postcode': region_postcode,
                    'region_name': region_name
                }
                if postcode_city_collection.find_one({'province_name': province_name, 'city_name': city_name, 'region_postcode': region_postcode, 'region_name': region_name}) is None:
                    postcode_city_collection.insert_one(data)
                    print('插入一条数据 {}'.format(data))
                else:
                    print('已经存在库中')
        else:
            print('没有找到相关信息')


class GetRegion(object):
    def __init__(self, proxies):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        self.proxies = proxies

    def get_province_city_region(self):
        for province_city in server_area.find(no_cursor_timeout=True):
            if 'province' in province_city:
                province = province_city['province']
                city = province_city['display']
                for region in region_block.find({'city': city, 'category': 'region'}):
                    if 'name' in region:
                        region_name = region['name']
                        self.get_postcode(province, city, region_name)
                    else:
                        print('库中没有区域')
            else:
                print('库中没有省份')

    def get_postcode(self, province, city, region_name):
        url = 'http://opendata.baidu.com/post/s?wd={}+{}+{}&p=mini&rn=20'.format(urllib.parse.quote(province.encode('gbk')), urllib.parse.quote(city.encode('gbk')), urllib.parse.quote(region_name.encode('gbk')))
        print(url)
        info_list = {
            'url': url,
            'city_name': city,
            'province_name': province,
            'region_name': region_name,
        }
        channel.basic_publish(exchange='',
                              routing_key='postcode',
                              body=json.dumps(info_list))
        print("放队列 {}".format(info_list))
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            r_text = r.content.decode('gbk')
            tree = etree.HTML(r_text)
            count_info = tree.xpath("//article[@class='mis-pager']/div/span/text()")[0]
            count = re.search('(\d+)', count_info).group(1)
            print(int(count) // 20)
            for i in range(1, (int(count) // 20) + 1):
                url = 'http://opendata.baidu.com/post/s?p=mini&wd={}%20{}%20{}&pn={}&rn=20'.format(urllib.parse.quote(province.encode('gbk')), urllib.parse.quote(city.encode('gbk')), urllib.parse.quote(region_name.encode('gbk')), 20 * i)
                print(url)
                info_list = {
                    'url': url,
                    'province_name': province,
                    'city_name': city,
                    'region_name': region_name,
                }
                channel.basic_publish(exchange='',
                                      routing_key='postcode',
                                      body=json.dumps(info_list))
                print("放队列 {}".format(info_list))
        except Exception as e:
            print('无信息')
