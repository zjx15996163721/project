"""
该函数的作用是将51job和拉钩两个网站剩下的无法放入到队列的进行格式化
"""
from pymongo import MongoClient
import yaml
import pika
from lib.standardization import standard_city,standard_region,StandarCityError
from lib.log import LogHandler
import gevent
from multiprocessing import Process

log = LogHandler('add_standar_fields')
client = MongoClient(host='114.80.150.196',
                     port=27777,
                     username='goojia',
                     password='goojia7102')
db = client['company']
collection = db['company_crawler']


def update_51job_fields():
    companys = collection.find({'company_source':'51job'},no_cursor_timeout=True)
    for company in companys[3376200:]:
        address = company['address']
        result, real_city = standard_city(address)
        if result:
            company['fj_city'] = real_city
            r, real_region = standard_region(real_city, address)
            if r:
                company['fj_region'] = real_region
            else:
                company['fj_region'] = None
        else:
            company['fj_city'] = None
            company['fj_region'] = None
        collection.update_one({'company_id':company['company_id'],'company_source':company['company_source']},{'$set':company})
        print('{}已经更新了'.format(company['company_id']))


def update_lagou_fields():
    companys = collection.find({'company_source': '拉钩'}, no_cursor_timeout=True)
    for company in companys[220000:]:
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
        elif city is None and address is not None and region is None:
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
        collection.update_one({'company_id': company['company_id'], 'company_source': company['company_source']},
                              {'$set': company})
        print('{}已经更新了'.format(company['company_id']))


if __name__ == '__main__':
    Process(target=update_lagou_fields).start()
    Process(target=update_51job_fields).start()

