import json
# from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import aiohttp
import asyncio
# from lib.log import LogHandler
# log = LogHandler('xiamen')
# p = Proxies()
# p = p.get_one(proxies_number=7)
# m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
# crawler_collection = m['hilder_gv']['xiamen']


class XiaMen:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }

    async def start(self):
        url = 'http://fdc.xmtfj.gov.cn:8001/home/Getzslp'
        for page in range(1, 51):
            data = {
                'currentpage': page,
                'pagesize': 20,
                'searchtj': '',
                'orderby': ''
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data, headers=self.headers) as response:
                    if response.status == 200:
                        await self.get_data(await response.text())

    async def get_data(self, r):
        info_list = json.loads(json.loads(r)['Body'])['bodylist']
        for info in info_list:
            name = info['XMMC']
            address = info['XMDZ']
            region = info['XMDQ']
            area = info['PZMJ']
            household_count = info['PZTS']
            data = {
                'source': 'xiamen',
                'city': '厦门',
                'region': region,
                'district_name': name,
                'complete_time': None,
                'household_count': household_count,
                'estate_charge': None,
                'address': address,
                'area': area,
                'estate_type2': '普通住宅',
            }
            print(data)
            # if not crawler_collection.find_one({'source': 'xiamen', 'city': '厦门', 'region': region, 'district_name': name,
            #                                     'complete_time': None, 'estate_charge': None, 'area': area,
            #                                     'household_count': household_count,
            #                                     'address': address, 'estate_type2': '普通住宅'}):
            #     crawler_collection.insert_one(data)
            #     log.info('插入一条数据{}'.format(data))
            # else:
            #     log.info('重复数据')


if __name__ == '__main__':
    x = XiaMen()
    asyncio.run(x.start())








