
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['fangjia']['seaweed_shanghai_hefei_wuxi_latest']
"""
estate_type2   普通住宅　别墅　商住

"""


def run():
    count = 0
    for i in crawler_collection.find():
        # if i['city'] == '上海':
        #     if i['estate_type2'] == '普通住宅' or i['estate_type2'] == '别墅' or i['estate_type2'] == '商住':
        #         if 'estate_charge' in i.keys():
        #             if i['estate_charge'] not in ['', ' ', None]:
        #                 print(i['estate_charge'])
        #                 count += 1
        if i['city'] == '上海':
            if i['estate_type2'] == '普通住宅':
                if 'estate_charge' in i.keys():
                    if i['estate_charge'] is not None:
                        if '~' in i['estate_charge']:
                            print(i['estate_charge'])
                            count += 1
                        elif i['estate_charge'] not in ['', ' ']:
                            if 0.0 < float(i['estate_charge']) < 10:
                                print(i['estate_charge'])
                                count += 1
                        else:
                            pass
            elif i['estate_type2'] == '别墅':
                if 'estate_charge' in i.keys():
                    if i['estate_charge'] not in ['', ' ', None]:
                        if float(i['estate_charge']) >= 3:
                            print(i['estate_charge'])
                            count += 1
            elif i['estate_type2'] == '商住':
                if 'estate_charge' in i.keys():
                    if i['estate_charge'] not in ['', ' ', None]:
                        if float(i['estate_charge']) >= 4:
                            print(i['estate_charge'])
                            count += 1
    print('上海有效的物业费为{}'.format(count))


def house():
    count = 0
    for i in crawler_collection.find():
        if i['city'] == '合肥':
            if i['estate_type2'] == '普通住宅':
                if 'household_count' in i.keys():
                    if i['household_count'] is not None:
                        if i['household_count'] not in ['', ' ']:
                            if 50 < int(i['household_count']) < 100000:
                                print(i['household_count'])
                                count += 1
            elif i['estate_type2'] == '别墅':
                if 'household_count' in i.keys():
                    if i['household_count'] is not None:
                        if i['household_count'] not in ['', ' ']:
                            if 20 < int(i['household_count']) < 100000:
                                print(i['household_count'])
                                count += 1
            elif i['estate_type2'] == '商住':
                if 'household_count' in i.keys():
                    if i['household_count'] is not None:
                        if i['household_count'] not in ['', ' ']:
                            if 50 < int(i['household_count']) < 100000:
                                print(i['household_count'])
                                count += 1
    print('有效的户数为{}'.format(count))


if __name__ == '__main__':
    run()