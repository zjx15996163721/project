"""
统计友达总价 和 面积乘单价的价格的差距
"""

from pymongo import MongoClient
from datetime import datetime
from elasticsearch import Elasticsearch

offline_deal_price = MongoClient(host='114.80.150.198', port=27017)
collection_offline = offline_deal_price['fangjia']['deal_price']

source_list = ['新友达', '友达']


# es = Elasticsearch()


def calculation():
    for source in source_list:
        for info in collection_offline.find({'source': source}, no_cursor_timeout=True):
            area = info['area']
            avg_price = info['avg_price']
            total_price = info['total_price']
            c_price = area * avg_price
            if abs(c_price - total_price) > 19999:
                print('area={},'
                      'avg_price={},'
                      'id={},'
                      '计算总价={},'
                      '总价={},'
                      '百分比={}%'.format(area,
                                       avg_price,
                                       info['_id'],
                                       c_price,
                                       total_price,
                                       int(abs(round(1 - c_price / total_price,
                                                     2) * 100))))

            # doc = {
            #     'name': info['district_name'],
            #     'city': info['city'],
            #     'avg_price': avg_price,
            #     'total_price': total_price,
            #     'number': int(abs(round(1 - c_price / total_price, 2) * 100))
            # }
            #
            # res = es.index(index="deal_price", doc_type='price', body=doc)
            # print(res['result'])
            # break


if __name__ == '__main__':
    calculation()
