"""
根据公司名称+城市+地址 去重
"""
from pymongo import MongoClient
import redis
import pika
import json
r = redis.Redis(host='localhost', port='6379')
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
company_crawler_collection = m['company']['company_crawler']
company_crawler_merge = m['company']['company_merge']
#
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
# channel = connection.channel()
# channel.queue_declare(queue='company_repeat')


def run():
    count = 0
    for i in company_crawler_collection.find(skip=2360688, no_cursor_timeout=True):
        count += 1
        print(count)
        try:
            company_name = i['company_name'].replace('\t', '').replace('\r', '').replace('\n', '')
            city = i['fj_city']
            company_name_city = company_name + city
            flag = r.sadd('company_name_city', company_name_city)
            if flag == 1:
                address_list = []
                address_list.append(i['address'])
                company_id_list = []
                company_id_list.append(i['company_id'])
                # 不重复的数据
                data = {
                    'company_name': i['company_name'],
                    'fj_city': i['fj_city'],
                    'address': address_list,
                    i['company_source']: company_id_list
                }
                print('{} 添加到redis，不重复的数据插入新表{}'.format(company_name_city, data))
                company_crawler_merge.insert_one(data)
            elif flag == 0:
                # 重复数据
                repeat_data = company_crawler_merge.find_one({'company_name': i['company_name'], 'fj_city': i['fj_city']})
                if repeat_data is not None:
                    repeat_data_address = repeat_data['address']
                    repeat_data_address.append(i['address'])
                    # 相同来源
                    if i['company_source'] in repeat_data.keys():
                        repeat_data_company_id = repeat_data[i['company_source']]
                        repeat_data_company_id.append(i['company_id'])
                        company_crawler_merge.find_one_and_update({'company_name': i['company_name'], 'fj_city': i['fj_city']}, {'$set': {i['company_source']: repeat_data_company_id, 'address': repeat_data_address}})
                        print('更新一条数据')
                    # 不同来源
                    else:
                        company_id_list = []
                        company_id_list.append(i['company_id'])
                        company_crawler_merge.find_one_and_update({'company_name': i['company_name'], 'fj_city': i['fj_city']}, {'$set': {i['company_source']: company_id_list, 'address': repeat_data_address}})
                        print('更新一条数据')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    run()

