# coding=gbk
import aiohttp
import asyncio
import json
from pymongo import MongoClient
from lib.log import LogHandler
log = LogHandler(__name__)
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_price = m['fangjiaguanjia']['price']


class GuanJiaPrice:

    def __init__(self):
        self.start_url = 'http://api.crevalue.cn/statis/v3/price/survey'
        self.headers = {
            'User-Agent': '%E6%88%BF%E4%BB%B7%E7%AE%A1%E5%AE%B6/2220 CFNetwork/902.2 Darwin/17.7.0'
        }
        self.proxies = 'http://FANGJIAHTT1:HGhyd7BF@http-proxy-sg2.dobel.cn:9180'
        self.info_list = []

    def update_no_price(self):
        count = 0
        for i in collection_price.find({'lease_price': None, 'sale_price': None}, no_cursor_timeout=True):
            count += 1
            print(count)
            if len(self.info_list) == 100:
                loop = asyncio.get_event_loop()
                tasks = [self.second_run(info) for info in self.info_list]
                loop.run_until_complete(asyncio.wait(tasks))
                self.info_list.clear()
            else:
                self.info_list.append(i)

        if len(self.info_list) > 0:
            loop = asyncio.get_event_loop()
            tasks = [self.second_run(info) for info in self.info_list]
            loop.run_until_complete(asyncio.wait(tasks))
            self.info_list.clear()

    async def second_run(self, info):
        await self.second_request(info)

    async def second_request(self, info):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.start_url,
                                   params={'apiKey': '2wU0pXPAlX5gpIEph9uvR5',
                                           'city': info['cityCode'],
                                           'distince': '1000',
                                           'ha': info['haCode'],
                                           'tradeType': 'lease_live,forsale_live',
                                           'version': '2.0',
                                           'propType': '11'},
                                   headers=self.headers) as response:
                if response.status == 200:
                    await self.second_get_info(await response.text(), info)
                else:
                    log.error('请求失败')

    async def second_get_info(self, r, info):
        price = json.loads(r)
        if price:
            await self.update_db(price, info)

    async def update_db(self, price, info):

        data = {
            'price_info': price,
            'cityCode': info['cityCode'],
            'city': info['city'],
            'region': info['region'],
            'name': info['name'],
            'haCode': info['haCode']
        }

        if 'leaseLive' in price:
            if 'unitPrice' in price['leaseLive']:
                data.update({'lease_price': price['leaseLive']['unitPrice']})
            else:
                data.update({'lease_price': None})
        else:
            data.update({'lease_price': None})

        if 'saleLive' in price:
            if 'unitPrice' in price['saleLive']:
                data.update({'sale_price': price['saleLive']['unitPrice']})
            else:
                data.update({'sale_price': None})
        else:
            data.update({'sale_price': None})

        collection_price.update_one({'haCode': info['haCode']}, {'$set': data})
        log.info('更新一条数据{}'.format(data))


if __name__ == '__main__':
    guanjia = GuanJiaPrice()
    guanjia.update_no_price()

