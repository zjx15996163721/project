import requests
from lib.mongo import Mongo
from lib.log import LogHandler
import time
import datetime
from lib.proxy_iterator import Proxies
p = Proxies()
P = p.get_one(proxies_number=3)
m = Mongo('114.80.150.196', 27777, user_name='goojia', password='goojia7102')
collection = m.connect['friends']['zhizi_list']
detail_collection = m.connect['friends']['zhizi_detail']
deal_price_collection = m.connect['friends']['zhizi_deal_price_new']
listing_price_collection = m.connect['friends']['zhizi_listing_price']
new_house_collection = m.connect['friends']['zhizi_new_house']
new_house_sales_license_collection = m.connect['friends']['zhizi_new_house_sales_license']

log = LogHandler(__name__)


def time_convert(data_):
    # 时间转换 '1532448000000'
    return time.strftime("%Y-%m-%d", time.localtime(data_ / 1000.0))


def price_convert(price_):
    # 价格转换 万元转元
    return int(price_) * 10000


headers = {
    'Cookie': 'ZHIZISESSION=b403cdae-49e4-48a3-8261-6dfd3d9b03d3; Hm_lvt_5c089e8c68a648496d81d499d82e8069=1542192069,1542192131; Hm_lpvt_5c089e8c68a648496d81d499d82e8069=1542192131',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}


class Zhizi:
    def __init__(self):
        pass

    def get_all_comm_name(self):
        """
        获取所有小区名
        :return:
        """
        r = requests.get(
            'http://exp.zhizishuku.com/110100/secondhouse/search/list.do?code=110100&name=&region=%E5%85%A8%E9%83%A8&regionType=%E5%85%A8%E5%B8%82&format=%E4%BD%8F%E5%AE%85%2C%E5%88%AB%E5%A2%85%2C%E5%85%AC%E5%AF%93&ageStart=&ageEnd=',
            headers=headers, proxies=P)
        result = r.json()
        for i in result['data']:
            if not collection.find_one({'id': i['id']}):
                log.info('新小区={}'.format(i))
                self.get_detail(i['name'])
                collection.insert_one(i)
            else:
                log.info('小区已存在={}'.format(i))

    def get_detail(self, comm_name):
        """
        小区详情
        :param comm_name:
        :return:
        """
        param = {
            'city': '110100',
            'name': comm_name
        }
        try:
            r = requests.post('http://exp.zhizishuku.com/110100/secondhouse/residentialDetails/baseInfo.do', data=param,
                              headers=headers, proxies=P)
            print(r.text)
            data = r.json()['data']
            data['sellDate'] = time_convert(data['sellDate'])
            data['completionDate'] = time_convert(data['completionDate'])
            if detail_collection.find_one({'residentialAreaName': data['residentialAreaName']}) is None:
                detail_collection.insert_one(data)
                print('插入一条小区详情={}'.format(data))
            else:
                log.info('小区详情已存在={}'.format(data))
        except Exception as e:
            log.info('小区详情入库失败={} e={}'.format(comm_name, e))

    def get_deal_and_listing_price(self, comm_name):
        # 成交
        url = 'http://exp.zhizishuku.com/110100/secondhouse/residentialDetails/caseInfo.do'
        case_type_list = ['成交', '挂牌']
        for case_type in case_type_list:
            data = {
                'city': '110100',
                'name': comm_name,
                'pageNo': 1,
                'pageSize': 1000,
                'caseType': case_type
            }
            try:
                r = requests.post(url=url, headers=headers, data=data, proxies=P)
                data = r.json()['data']
            except Exception as e:
                log.info('{}错误，小区名={}'.format(case_type, comm_name))
                continue
            if r.json()['data'] is None:
                continue
            if case_type is '成交':
                for deal_price in data['cases']:
                    deal_price['comm_name'] = comm_name
                    deal_price['totalPrice'] = price_convert(deal_price['totalPrice'])
                    deal_price.update({'crawler_time': datetime.datetime.now()})
                    if not deal_price_collection.find_one({'comm_name': deal_price['comm_name'],
                                                           'caseTime': deal_price['caseTime'],
                                                           'area': deal_price['area'],
                                                           'price': deal_price['price'],
                                                           'roomType': deal_price['roomType'],
                                                           'totalPrice': deal_price['totalPrice']}):
                        deal_price_collection.insert(deal_price)
                        log.info('新的成交数据={}'.format(deal_price))
                    else:
                        log.info('数据库已经存在本次成交={}'.format(deal_price))
            else:
                for listing_price in data['cases']:
                    listing_price['comm_name'] = comm_name
                    listing_price['totalPrice'] = price_convert(listing_price['totalPrice'])
                    listing_price['caseTime'] = time_convert(listing_price['caseTime'])
                    listing_price.update({'crawler_time': datetime.datetime.now()})
                    if not listing_price_collection.find_one({'comm_name': listing_price['comm_name'],
                                                              'caseTime': listing_price['caseTime'],
                                                              'area': listing_price['area'],
                                                              'price': listing_price['price'],
                                                              'roomType': listing_price['roomType'],
                                                              'totalPrice': listing_price['totalPrice']}):
                        listing_price_collection.insert(listing_price)
                        log.info('新的挂牌数据={}'.format(listing_price))
                    else:
                        log.info('数据库已经存在本次挂牌={}'.format(listing_price))


class ZhiZiNewHouse:
    def __init__(self):
        pass

    def get_new_room(self):
        new_room_list_url = 'http://exp.zhizishuku.com/110100/secondhouse/newroom/newRoomSalesAmount.do?cityCode=110100&marketType=1&countType=1'
        try:
            response = requests.get(url=new_room_list_url, headers=headers, proxies=P)
        except Exception as e:
            log.error('请求失败 url={}, e={}'.format(new_room_list_url, e))
            return
        house_list = response.json()
        for house_info in house_list['data']:
            house_info['totalmoney'] = price_convert(house_info['totalmoney'])
            house_id = house_info['id']
            if not new_house_collection.find_one({'id': house_id}):
                # 详情
                new_room_info_url = 'http://exp.zhizishuku.com/110100/secondhouse/project/project.do'
                data = {
                    'cityCode': '110100',
                    'projectCode': str(house_id)
                }
                try:
                    response1 = requests.post(url=new_room_info_url, headers=headers, data=data, proxies=P)
                except Exception as e:
                    log.error('请求失败 url={}, e={}'.format(new_room_info_url, e))
                    continue
                detail = response1.json()['data']
                house_info['detail'] = detail
                house_info.update({'crawler_time': datetime.datetime.now()})
                new_house_collection.insert_one(house_info)
                print('插入一条新数据={}'.format(house_info))
            else:
                log.info('小区已存在={}'.format(house_id))

            # 销售许可
            new_room_sales_license_url = 'http://exp.zhizishuku.com/110100/secondhouse/project/projectPin.do'
            data = {
                'cityCode': '110100',
                'projectCode': str(house_id)
            }
            try:
                response2 = requests.post(url=new_room_sales_license_url, headers=headers, data=data, proxies=P)
                info = response2.json()['data']
            except Exception as e:
                log.error('请求失败 url={}, house_id={}, e={}'.format(new_room_sales_license_url, house_id, e))
                continue
            if info is None:
                continue
            for sales_license in info:
                if not new_house_sales_license_collection.find_one(
                        {'FaZhengShiJian': sales_license['FaZhengShiJian'],
                         'GongYingMianJi': sales_license['GongYingMianJi'],
                         'GongYingTaoShu': sales_license['GongYingTaoShu'],
                         'XiaoShouLouHao': sales_license['XiaoShouLouHao']}):
                    sales_license['houseId'] = house_id
                    sales_license.update({'crawler_time': datetime.datetime.now()})
                    new_house_sales_license_collection.insert_one(sales_license)
                    print('插入一条新销售许可证={}'.format(sales_license))
                else:
                    log.info('数据库已经存在这个销售许可证={}'.format(sales_license))


if __name__ == '__main__':
    # z = Zhizi()
    # for i in collection.find():
    #     z.get_detail(i['name'])

    # for i in collection.find():
    #     z.get_deal_and_listing_price(i['name'])

    n = ZhiZiNewHouse()
    n.get_new_room()