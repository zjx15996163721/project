import re
import requests
from lib.log import LogHandler
import pika
import yaml
import json
from pymongo import MongoClient
import gevent
from lib.standardization import standard_city,standard_region,StandarCityError
import asyncio
import aiohttp
import time
from multiprocessing import Process

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='114.80.150.195',
    port=5673,
    heartbeat=0
))
channel = connection.channel()
channel.queue_declare(queue='lagou_id')

client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102')
db = client['company']
collection = db['company_crawler']


def lagou_start_produce():
    companys = collection.find({'company_source': "拉钩"}, no_cursor_timeout=True)
    id_list = []
    for company in companys:
        company_id = company['company_id']
        id_list.append(company_id)
        if len(id_list) == 200:
            channel.basic_publish(
                exchange='',
                routing_key='lagou_id',
                body=json.dumps(id_list)
            )
            id_list.clear()

class LagouConsumer:
    def start_consume(self):
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(
            self.callback,
            queue='lagou_id'
        )
        channel.start_consuming()

    # def callback(self, ch, method, properties, body):
    #     ids = json.loads(body.decode())
    #     jobs = [gevent.spawn(self.update_fields, id) for id in ids]
    #     gevent.joinall(jobs)
    #     ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback(self, ch, method, properties, body):
        ids = json.loads(body.decode())
        loop = asyncio.get_event_loop()
        tasks = [self.start_async(id) for id in ids]
        loop.run_until_complete(asyncio.wait(tasks))
        ch.basic_ack(delivery_tag=method.delivery_tag)


    async def start_async(self,id):
        await self.update_data(await self.standar_address(await self.find_mongo(id)))

    async def find_mongo(self,id):
        company = collection.find_one({'company_source': "拉钩", 'company_id': id}, no_cursor_timeout=True)
        return company

    async def standar_address(self,company):
        address = company['address']
        city = company['city']
        region = company['region']
        if city is not None and region is not None and address is not None:
            address_string = city + region + address
        elif city is not None and address is not None and region is None:
            address_string = city + address
        elif city is None and address is not None and region is not None:
            address_string = address + region
        elif city is not None and region is not None and address is None:
            address_string = city + region
        elif city is None and address is not None and region is  None:
            address_string = address
        elif city is not None and region is None and address is None:
            address_string = city
        else:
            address_string = ''
        result, real_city = standard_city(address_string)
        if result:
            company['fj_city'] = real_city
            r, real_region = standard_region(real_city, address_string)
            if r:
                company['fj_region'] = real_region
            else:
                company['fj_region'] = None
        else:
            company['fj_city'] = None
            company['fj_region'] = None
        return company

    async def update_data(self,company):
        collection.update_one({'company_id': company['company_id'], 'company_source': company['company_source']},
                              {'$set': company})
        print('{}已经更新了'.format(company['company_id']))


    # def update_fields(self,id):
    #     company = collection.find_one({'company_source': '51job','company_id':id}, no_cursor_timeout=True)
    #     # print(company)
    #     address = company['address']
    #     result, real_city = standard_city(address)
    #     if result:
    #         company['fj_city'] = real_city
    #         r, real_region = standard_region(real_city, address)
    #         if r:
    #             company['fj_region'] = real_region
    #         else:
    #             company['fj_region'] = None
    #     else:
    #         company['fj_city'] = None
    #         company['fj_region'] = None
    #     collection.update_one({'company_id': company['company_id'], 'company_source': company['company_source']},
    #                           {'$set': company})
    #     print('{}已经更新了'.format(company['company_id']))


if __name__ == '__main__':
    # lagou_start_produce()
    Process(target=LagouConsumer().start_consume).start()
    Process(target=LagouConsumer().start_consume).start()




