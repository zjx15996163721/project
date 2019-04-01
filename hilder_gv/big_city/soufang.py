import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
import aiohttp
import asyncio
from lib.log import LogHandler
import time
import pika
import json
log = LogHandler('soufang')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['fangjia']['district_complete']


class SouFang:

    def __init__(self):
        self.headers = {
            'Cookie': 'UM_distinctid=166f290faac6cf-01ce96135d9f9b-3c7f0257-1fa400-166f290faae793; uniqueName=24b8a77140e1d26f7569dbcfb1ee67a6; sale_rent_sb_1=eyJpdiI6IkRXekdFcjNTTUtRaHM3Zm13QjJxbWc9PSIsInZhbHVlIjoickJXWllRNFpIYmJRcVJZQkJCc1Y5dz09IiwibWFjIjoiZDI4NmM3YmI5YTU4OWE2NzkxNDdmMDJmN2YwOGI5ZjM4MTcwMmQ1Mjk5ZGY3MmFhODRkYWFjNDA0MzI2ZjM0NCJ9; sale_rent_sb_26=eyJpdiI6IlkxV0tqMWI3TGJxcVZ3eWNiYXp5NlE9PSIsInZhbHVlIjoiS0ZDUTNOQjhBTjlnVWI2MklTRGxMQT09IiwibWFjIjoiYTQxY2NlMTVkZmUzOTdiZDkxZjkwNDZlMTIxMzM5Y2NjOTQyZDRkMWIwNTI5MzhlN2E2YzdhMTM3ZjEwMGY2OSJ9; CNZZDATA1262285598=1095956314-1542262748-%7C1543216077; sale_rent_sb_334=eyJpdiI6Ikc5M2l4aVFRQVVWZVlCNzQwZzRPT1E9PSIsInZhbHVlIjoiUk1Ra1Rvakx0S0NlQ21BcDFnWnRydz09IiwibWFjIjoiNGE0MGM5YjhjYjcyNjgwMjRkYjU2NTg1MGViZWZlNjVmMmI3NzE0YzYwYTFjYjMxOWVjNDRhYmNiNGYzMjhlMiJ9; XSRF-TOKEN=eyJpdiI6IlBJWTE2Q0RmR2x6SCtVS0JqTng2U3c9PSIsInZhbHVlIjoiaXVaTmdmZ3lJR1h5blhkWDI4YiswVHBqSEZTUVAzK29jNk1CcWdIZStLcGZOZzBHbnBOcVRqRUxwUkhWcmlsblwvSExtWnYxMU9kVzFkM2ViZ1hCOHd3PT0iLCJtYWMiOiJjYTcwMWQ1YTRlMmVmZWM0OWI2ZmVmOGI0NzFkZjZmYmExOGVmYjVlOTNjYjczNThmNGY3YThjYmUxMmE4MGU2In0%3D; www_sofang_session=eyJpdiI6Img1N2JlYzE3NHZFMmJXWUxmOVQwcWc9PSIsInZhbHVlIjoiXC9Kb2Y1M1g1WHYzdSthUEg0ZUJwQTdJOTFrVUc0NUk2SnZrU1J0bnlDVTU5dkgzbTRsdW54QTFzZzlqM1l5aDk5XC9TN0krXC9HU1RTb1BqOHZGZGdsZmc9PSIsIm1hYyI6ImU3NGE1YWM1ZWEwYWJmOTNlMWJhODk2ZjE5NGI4NGM1Y2RiNjM4Yzk4ZjU2NjhjM2U0ZTQwYzk5OWZlNDgzMGQifQ%3D%3D; cityid=eyJpdiI6ImlWRCtDXC9WQ05VcFA1TW5UeWZQbytBPT0iLCJ2YWx1ZSI6IjRQV0thK1RObWZIVitGUXZQbFErQmc9PSIsIm1hYyI6ImUxMzhiN2RkYjRmZTdjODA2YzhiZGNhZTIwNDEzNzk3ZDVlMTk2NDQyZWM0ZTk2ZmJjZGUxMzQyMWYxMzcyM2YifQ%3D%3D; city=eyJpdiI6IldcL25yZUxKWFJZUGdiV05mUjJIcHNnPT0iLCJ2YWx1ZSI6IjhPeXhFTHg5cXArc1pMR0lhUzNGRmN3cXpcL09FOVJ4NDNHaHh2NnlmS0pmY0pLR3M3aFppeGFUWU00WCtWYVpCaVU5cmNHR1N4SkFUYVpXOVNuVzZEUmhRV2tLdllGQkJpa2NLRm5MOWZ1RUFZekxYWUJFVDBDWE9laExRYU53VUhOTlJPSmdvRWkya0R4MUpORDJUR2lKNWlOZTZFeFBhSUs3WGc0WHdveHNZV0Fhb3hibEVGM1R1aEl4SkV2cmxzXC9sZnlCTFJyXC9MYU1ZXC9OOVVRZk5PalpCZzh6dkw3V0gxeUxkNHM3eXdyZ01OU2pmSlYyR3E4Z0drWGpQWnc3WWh2RXMyd2JWbEllTVFUN1EyTUVJQXg4SWRFZkc2UVhyb3JMRVdCN0lCdz0iLCJtYWMiOiJjZmU5YzVmMTBkMTE3MTVjMzc3ZGE1MTY2NzVjNDM4YTJmODUxYjk5YmU4NTU1YjlhYWUwYTVhZWRlZGNjY2UzIn0%3D; citypy=eyJpdiI6Ilo0SG41YnRGUTBCbVB6bkxvWHJ0QXc9PSIsInZhbHVlIjoiSDhRV3RmY1JBZ0p4YVhlMEtpMFRhUT09IiwibWFjIjoiODc5NWRmODQ4YTYzNDQ2ZGU3OGU3NTUzMWYyNTNhZDg2YWZjZDEzZjg1MjY2OWE0N2YyYzcwOGQ5NzdlMTc3ZSJ9',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='soufang')
        self.start_url = [('http://wx.sofang.com/saleesb/area', 115), ('http://hf.sofang.com/saleesb/area', 141)]

    def start_crawler(self):
        for i in self.start_url:
            url = i[0]
            max_page = i[1]
            for page in range(1, int(max_page)+1):
                page_url = url + '/bl{}?'.format(str(page))
                self.get_all_url(page_url)

    def get_all_url(self, page_url):
        try:
            r = requests.get(url=page_url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        try:
            tree = etree.HTML(r.text)
            url_info_list = tree.xpath('/html/body/div[4]/div[4]/div[1]/div[2]/dl')
        except Exception as e:
            log.error(e)
            return
        for info in url_info_list:
            half_url = info.xpath('./dd[1]/p/a/@href')[0]
            url = re.search('(http://.*?\.sofang\.com)', page_url, re.S | re.M).group(1) + half_url
            self.channel.basic_publish(exchange='',
                                       routing_key='soufang',
                                       body=json.dumps(url))
            log.info('放队列 {}'.format(url))


if __name__ == '__main__':
    soufang = SouFang()
    soufang.start_crawler()