#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 12:20
# @Author  : Alex
# @Email   : zhangjinxiao@fangjia.com
# @File    : city.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup

def response():
    try:
        url = 'http://news.sh.fang.com/'
        #设置请求头
        headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive'
                    }
        response = requests.get(url=url, headers=headers)
        response.encoding = 'GBK'
        return response
    except Exception as e:
        print(e)

def gethtml():
    try:
        #解析
        text = response().text
        soup = BeautifulSoup(text, 'lxml')
        return soup
    except Exception as e:
        print(e)

#获取所以的城市链接
def get_All_City():
    try:
        html = gethtml()
        cityLinks1 = html.select('#cityi011 > a')
        cityLinks2 = html.select('#cityi012 > a')
        cityLinks3 = html.select('#cityi013 > a')
        list1 = cityLinks1 + cityLinks2 + cityLinks3
        list2 = []
        for link in list1:
            links = link.get('href')
            list2.append(links)
        return list2
    except Exception as e:
        print(e)


