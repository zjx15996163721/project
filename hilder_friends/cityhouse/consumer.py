import json
import pika
import yaml
import aiohttp
import asyncio
from lxml import etree
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
from lib.mongo import Mongo
import datetime

log = LogHandler(__name__)
p = Proxies()
setting = yaml.load(open('config.yaml'))

rabbit_host = setting['cityhouse']['rabbit']['host']
rabbit_port = setting['cityhouse']['rabbit']['port']
mongo_host = setting['cityhouse']['mongo']['host']
mongo_port = setting['cityhouse']['mongo']['port']
user_name = setting['cityhouse']['mongo']['user_name']
password = setting['cityhouse']['mongo']['password']
db_name = setting['cityhouse']['mongo']['db']
db_coll = setting['cityhouse']['mongo']['comm_coll']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))

m = Mongo(host=mongo_host, port=mongo_port, user_name=user_name, password=password)
collection = m.connect[db_name][db_coll]
collection.create_index('co_id', unique=True)
proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
                "host": "http-proxy-sg2.dobel.cn",
                "port": "9180",
                "account": 'FANGJIAHTT8',
                "password": "HGhyd7BF",
            }
proxies = {"https": proxy,
                       "http": proxy}

class CityHouseConsume:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36'
        }

    def start_consume(self):
        channel = connection.channel()
        channel.basic_qos(prefetch_count=20)
        channel.basic_consume(consumer_callback=self.callback, queue='cityhouse')
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        comm_list = json.loads(body.decode())
        semaphore = asyncio.Semaphore(50)
        loop = asyncio.get_event_loop()
        tasks = [self.consume(soul, semaphore) for soul in comm_list]
        loop.run_until_complete(asyncio.wait(tasks))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    async def fetch(self, soul, semaphore):
        citycode = soul['city_code']
        comm_id = soul['comm_id']
        city_name = soul['city_name']
        url = 'http://{}.cityhouse.cn/webservice/fythadetail.html?id={}&apiKey=4LiEDwxaRaAYTA3GBfs70L&ver=2'.format(
            citycode, comm_id
        )
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, headers=self.headers, proxy=next(p)['http']) as resp:
                        if resp.status < 300:
                            con = await resp.read()
                            return con, city_name, comm_id
                        else:
                            log.error('{}请求失败,status_code={}'.format(url, resp.status))
                            return None
                except Exception as e:
                    log.error('url={},请求失败,error={}'.format(url, e))

    async def consume(self, soul,semaphore):
        result = await self.fetch(soul,semaphore)
        if result is None:
            return
        data, city_name, co_id = await   self.fetch(soul,semaphore)
        cityname = city_name
        name = await self.parse(data, '//name/text()')
        district = await self.parse(data, '//district/text()')
        street = await self.parse(data, '//street/text()')
        comm_type = await self.parse(data, '//incomehouse/text()')
        kpdate = await self.parse(data, '//kpdate/text()')
        location = await self.parse(data, '//location/text()')
        build_size = await self.parse(data, '//item[@name="建筑面积"]/text()')
        land_size = await self.parse(data, '//item[@name="占地面积"]/text()')
        green_rate = await self.parse(data, '//item[@name="绿化率"]/text()')
        volumetric_rate = await self.parse(data, '//item[@name="容积率"]/text()')
        fee = await self.parse(data, '//item[@name="物业费"]/text()')
        certificate = await self.parse(data, '//item[@name="证件信息"]/text()')
        develop_company = await self.parse(data, '//item[@name="开发商"]/text()')
        property_company = await self.parse(data, '//item[@name="物业公司"]/text()')
        build_end_time = await self.parse(data, '//phases/@t')
        html_info = data.decode().encode()
        crawler_time = datetime.datetime.now()

        info = {'comm_name': name, 'district': district, 'street': street, 'type': comm_type,
                'kpdate': kpdate, 'location': location, 'build_size': build_size,
                'land_size': land_size, 'green_rate': green_rate, 'volumetric_rate': volumetric_rate,
                'fee': fee, 'certificate': certificate, 'develop_company': develop_company,
                'property_company': property_company, 'city': cityname, 'co_id': co_id,
                'build_end_time': build_end_time, 'html_info': html_info,
                'crawler_time': crawler_time}
        collection.update_one({'co_id': co_id}, {'$set': info}, upsert=True)
        log.info('已更新小区={},info={}'.format(name, info))

    @staticmethod
    async def parse(data, regx):
        """
        xpath解析
        :param data: 解析对象（bytes）
        :param regx:xpath解析规则
        :return:
        """
        result = etree.HTML(data.decode().encode())
        if len(result.xpath(regx)) == 0:
            return None
        else:
            return result.xpath(regx)[0]
