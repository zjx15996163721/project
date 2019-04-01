from lxml import etree
# from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import aiohttp
import asyncio
# from lib.log import LogHandler
# log = LogHandler('qingdao')
# p = Proxies()
# p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

# m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
# crawler_collection = m['hilder_gv']['qingdao']

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
}


async def start_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, verify_ssl=False) as response:
            if response.status == 200:
                await get_detail_url(await response.text())


async def start():
    for page in range(1, 139):
        url = 'https://www.qdfd.com.cn/qdweb/realweb/fh/FhProjectQuery.jsp?selState=2&page=' + str(page) + '&rows=20&okey=&order='
        await start_request(url)


async def get_detail_url(r):
    tree = etree.HTML(r)
    info_list = tree.xpath('//div[@class="cxlb"]/ul[2]//tr')
    for info in info_list[1:-1]:
        name = info.xpath('./td[2]/a/text()')[0]
        address = info.xpath('./td[3]/text()')[0]
        household_count = info.xpath('./td[4]/text()')[0]
        area = info.xpath('./td[5]/text()')[0]
        region = info.xpath('./td[7]/text()')[0]
        data = {
            'source': 'qingdao',
            'city': '青岛',
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
        # if not crawler_collection.find_one({'source': 'qingdao', 'city': '青岛', 'region': region, 'district_name': name,
        #                                     'complete_time': None, 'estate_charge': None, 'area': area, 'household_count': household_count,
        #                                     'address': address, 'estate_type2': '普通住宅'}):
        #     crawler_collection.insert_one(data)
        #     log.info('插入一条数据{}'.format(data))
        # else:
        #     log.info('重复数据')


if __name__ == '__main__':
    asyncio.run(start())



