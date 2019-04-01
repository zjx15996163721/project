#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/17 10:17
# @Author  : Alex
# @Email   : zhangjinxiao@fangjia.com
# @File    : __init__.py.py
# @Software: PyCharm
import requests
import re
def more(url):
    try:
        headers = {
            'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.nbd.com.cn',
            'If-None-Match': '06df643755a61c9c13a31fb74d27437b',
            'Referer': 'http://www.nbd.com.cn/fangchan',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
            'X-CSRF-Token': '+qYhSliyi8ZV2tLBI+HES72WeuOwOkp1yIP6A+8SgLk=',
            'X-Requested-With': 'XMLHttpRequest'
        }

        response = requests.get(url=url, headers=headers)
        info = response.text.replace(' ', '')
        link = re.search('href="(http://www\.nbd\.com\.cn/columns/298\?last_article=\d+&version_column=v5)', info).group(1)
        print(link)
        more(link)
        return link
    except Exception as e:
        print(e)
url = 'http://www.nbd.com.cn/columns/298?last_article=1217292&version_column=v5'
more(url)



