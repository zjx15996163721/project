#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2018/6/30 22:33
# @Author  : Alex
# @Email   : 1735429225@qq.com
# @File    : index16.py
# @Software: PyCharm
import requests
import json


class Xima(object):
    def __init__(self, bookname):
        self.book_name = bookname
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
        }
        self.start_url = "https://www.ximalaya.com/revision/play/album?albumId=2897626&pageNum={}&sort=-1&pageSize=30"
        self.book_url = []
        for i in range(51):
            url = self.start_url.format(i+1)
            self.book_url.append(url)

    def get_book(self):
        all_list = []
        for url in self.book_url:
            response = requests.get(url=url, headers=self.headers)
            all_dict = json.loads(response.content.decode())
            book_list = all_dict['data']['tracksAudioPlay']
            for book in book_list:
                list = {}
                list['title'] = book['trackName']
                list['url'] = book['src']
                # print(list)
                all_list.append(list)
        return all_list

    def save(self, all_list):
        for i in all_list:
            print(i)
            with open('Xima/{}.m4a'.format(self.book_name + i['title']), 'ab') as f:
                r = requests.get(url=i['url'], headers=self.headers)
                f.write(r.content)

    def run(self):
        all_list = self.get_book()
        self.save(all_list)


if __name__ == '__main__':
    Xima = Xima('全职高手')
    Xima.run()





