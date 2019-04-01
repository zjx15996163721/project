import requests
from lxml import etree
import re
from lib.log import LogHandler
import pika
import json
import yaml
import time
log = LogHandler('wangyi')
setting = yaml.load(open('wangyi_config.yaml'))
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'],
                                                               port=setting['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='wangyi')


class WangYi:

    def __init__(self, proxies):
        self.headers = {
            'Host': 'data.house.163.com',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': 'vjuids=141315b71.16778fc86e6.0.7a85a7026d79a; _ntes_nnid=d03c289051f2bddb3c1f67707d0a284c,1543923075313; _ntes_nuid=d03c289051f2bddb3c1f67707d0a284c; City=021; Province=021; ne_analysis_trace_id=1544081185373; s_n_f_l_n3=7626d82a149b92421544081185381; HOUSE_USER_MEMBER_SESSION_ID=HOUSE_USER_MEMBER_SESSION_ID-2be2732670ff4dfb167ff6671307bd82ce9793ae-72d1-4366-a74d-059fe47b41a6; hb_MA-A924-182E1997E62F_source=data.house.163.com; _antanalysis_s_id=1544081186455; pgr_n_f_l_n3=7626d82a149b924215441995801872302; vinfo_n_f_l_n3=7626d82a149b9242.1.0.1544081185381.0.1544199582203; vjlast=1543923075.1544422624.11',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        }
        self.proxies = proxies
        self.date = {
            '201704': '2017.04.01-2017.04.30',
            '201705': '2017.05.01-2017.05.31',
            '201706': '2017.06.01-2017.06.30',
            '201707': '2017.07.01-2017.07.31',
            '201708': '2017.08.01-2017.08.31',
            '201709': '2017.09.01-2017.09.30',
            '201710': '2017.10.01-2017.10.31',
            '201711': '2017.11.01-2017.11.30',
            '201712': '2017.12.01-2017.12.31',
            '201801': '2018.01.01-2018.01.31',
            '201802': '2018.02.01-2018.02.28',
            '201803': '2018.03.01-2018.03.31',
            '201804': '2018.04.01-2018.04.30',
            '201805': '2018.05.01-2018.05.31',
            '201806': '2018.06.01-2018.06.30',
            '201807': '2018.07.01-2018.07.31',
            '201808': '2018.08.01-2018.08.31',
            '201809': '2018.09.01-2018.09.30',
            '201810': '2018.10.01-2018.10.31',
            '201811': '2018.11.01-2018.11.30'
        }
        self.start_url_list = [
                               ('http://data.house.163.com/bj/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                               ('http://data.house.163.com/gz/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                               ('http://data.house.163.com/st/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                               ('http://data.house.163.com/nb/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                               ('http://data.house.163.com/sh/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                               ('http://data.house.163.com/hn/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '海南'),
                               ('http://data.house.163.com/nj/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                               ('http://data.house.163.com/fs/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                               ('http://data.house.163.com/zh/housing/xx/plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                               ]

    def start_crawler(self):
        for start_url in self.start_url_list:
            url = start_url[0]
            city = start_url[1]
            for date in self.date:
                month_url = re.search('(.*?plate/%E4%B8%8D%E9%99%90/%E4%B8%8D%E9%99%90/)', url, re.S | re.M).group(1) + self.date[date] + '/todayflat/desc/1.html'
                self.get_next_page(month_url, city, date)

    def get_next_page(self, url, city, date):
        page = 0
        while True:
            url = re.search('(.*?desc/)', url, re.S | re.M).group(1) + str(page+1) + '.html'
            try:
                r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                log.error('请求失败 url={}, e={}'.format(url, e))
                page += 1
                continue
            tree = etree.HTML(r.text)
            info_list = tree.xpath('//*[@id="resultdiv_1"]/table/tbody/tr')
            print(len(info_list))
            if len(info_list) > 3:
                data = {
                    'url': url,
                    'city': city,
                    'date': date
                }
                channel.basic_publish(exchange='',
                                      routing_key='wangyi',
                                      body=json.dumps(data))
                log.info('放队列 {}'.format(data))
                page += 1
            else:
                break









"""
self.ur_list = [('http://data.house.163.com/bj/housing/xx/plate/%E6%9C%9D%E9%98%B3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E6%B5%B7%E6%B7%80/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E4%B8%B0%E5%8F%B0/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E7%9F%B3%E6%99%AF%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E9%80%9A%E5%B7%9E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E5%A4%A7%E5%85%B4/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E6%98%8C%E5%B9%B3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E9%A1%BA%E4%B9%89/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E6%88%BF%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E4%B8%9C%E5%9F%8E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E8%A5%BF%E5%9F%8E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E9%97%A8%E5%A4%B4%E6%B2%9F/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E6%80%80%E6%9F%94/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E5%AF%86%E4%BA%91/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E5%B9%B3%E8%B0%B7/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/bj/housing/xx/plate/%E5%BB%B6%E5%BA%86/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '北京'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E5%A4%A9%E6%B2%B3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E6%B5%B7%E7%8F%A0/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E8%B6%8A%E7%A7%80/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E8%8D%94%E6%B9%BE/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E7%99%BD%E4%BA%91/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E9%BB%84%E5%9F%94/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E7%95%AA%E7%A6%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E8%8A%B1%E9%83%BD/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E5%8D%97%E6%B2%99/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E5%A2%9E%E5%9F%8E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/gz/housing/xx/plate/%E4%BB%8E%E5%8C%96/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '广州'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E9%87%91%E5%B9%B3%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E9%BE%99%E6%B9%96%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E6%BF%A0%E6%B1%9F%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E6%BD%AE%E9%98%B3%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E6%BD%AE%E5%8D%97%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E5%8D%97%E6%BE%B3%E5%8E%BF/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/st/housing/xx/plate/%E6%BE%84%E6%B5%B7%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '汕头'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E9%84%9E%E5%B7%9E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E6%B1%9F%E4%B8%9C/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E6%B5%B7%E6%9B%99/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E5%8C%97%E4%BB%91/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E6%B1%9F%E5%8C%97/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E9%95%87%E6%B5%B7/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E6%85%88%E6%BA%AA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E4%BD%99%E5%A7%9A/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E8%B1%A1%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E5%A5%89%E5%8C%96/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E9%AB%98%E6%96%B0%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E5%AE%81%E6%B5%B7/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/nb/housing/xx/plate/%E4%B8%9C%E9%92%B1%E6%B9%96/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '宁波'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E6%B5%A6%E4%B8%9C/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E9%97%B5%E8%A1%8C/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E6%9D%BE%E6%B1%9F/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E5%98%89%E5%AE%9A/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E6%99%AE%E9%99%80/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E5%AE%9D%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E6%9D%A8%E6%B5%A6/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E8%99%B9%E5%8F%A3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E5%BE%90%E6%B1%87/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E9%95%BF%E5%AE%81/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E9%BB%84%E6%B5%A6/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E6%96%B0%E9%9D%99%E5%AE%89/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E5%A5%89%E8%B4%A4/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E9%9D%92%E6%B5%A6/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E9%87%91%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/sh/housing/xx/plate/%E5%B4%87%E6%98%8E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '上海'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E9%BC%93%E6%A5%BC/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E7%A7%A6%E6%B7%AE/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E7%8E%84%E6%AD%A6/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E5%BB%BA%E9%82%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E9%9B%A8%E8%8A%B1%E5%8F%B0/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E6%B5%A6%E5%8F%A3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E6%B1%9F%E5%AE%81/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E6%A0%96%E9%9C%9E/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E5%85%AD%E5%90%88/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E9%AB%98%E6%B7%B3/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E6%BA%A7%E6%B0%B4/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/nj/housing/xx/plate/%E5%8D%97%E4%BA%AC%E5%91%A8%E8%BE%B9/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '南京'),
                        ('http://data.house.163.com/fs/housing/xx/plate/%E9%A1%BA%E5%BE%B7%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                        ('http://data.house.163.com/fs/housing/xx/plate/%E7%A6%85%E5%9F%8E%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                        ('http://data.house.163.com/fs/housing/xx/plate/%E5%8D%97%E6%B5%B7%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                        ('http://data.house.163.com/fs/housing/xx/plate/%E4%B8%89%E6%B0%B4%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                        ('http://data.house.163.com/fs/housing/xx/plate/%E9%AB%98%E6%98%8E%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '佛山'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%85%B6%E5%AE%83%E5%9F%8E%E5%B8%82/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E4%B8%AD%E5%B1%B1%E5%85%B6%E4%BB%96%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E9%87%91%E6%B9%BE/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E6%A8%AA%E7%90%B4%E6%96%B0%E5%8C%BA/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E4%B8%89%E4%B9%A1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%9D%A6%E6%B4%B2/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E6%96%97%E9%97%A8/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%94%90%E5%AE%B6/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%8D%97%E6%B9%BE/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%89%8D%E5%B1%B1/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E5%90%89%E5%A4%A7/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E6%8B%B1%E5%8C%97/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E9%A6%99%E6%B4%B2/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ('http://data.house.163.com/zh/housing/xx/plate/%E6%96%B0%E9%A6%99%E6%B4%B2/%E4%B8%8D%E9%99%90/2014.01.01-2018.12.31/todayflat/desc/1.html', '珠海'),
                        ]
                        
                        
                        
    # def get_city(self):
    #     for i in self.ur_list:
    #         for j in range(1, 100):
    #             link = re.search('(.*?desc/)', i[0]).group(1) + str(j) + '.html'
    #             data = {
    #                 'url': link,
    #                 'city': i[1]
    #             }
    #             channel.basic_publish(exchange='',
    #                                   routing_key='wangyi',
    #                                   body=json.dumps(data))
    #             log.info('放队列 {}'.format(data))
"""