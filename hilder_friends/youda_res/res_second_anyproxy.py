import requests
import json

from pymongo import MongoClient
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['deal_price']['res_second_2018_10']


class Anyproxy:

    def __init__(self):
        self.anyproxy = "http://localhost:8002/latestLog"

    def get_data(self):
        for id in range(1, 10000):
            url = 'http://localhost:8002/fetchBody?id=' + str(id)
            comm_res = requests.get(url)
            print(comm_res.text)
            com_dict = comm_res.json()
            print(com_dict)
            """
            # 数据字段
            acreage: 107.53
            adjustafteraddress: "赤峰路59弄2*号10*"
            area: "杨浦"
            buymarketprice: 82310
            buymarketusd: 8850794.3.png
            corporation: "上海欣慧房地产"
            corporationtype: "中介"
            fullhousingname: "书香公寓"
            houseaddress: "赤峰路59弄23号102"
            housetrait: ""
            housetype: "公寓"
            housingaddressall: "赤峰路59弄"
            marketprice: 80252
            marketusd: 8629497.56
            module: "内环以内"
            newdiskid: 11688
            newdiskname: "书香公寓2004"
            plate: "鞍山"
            propertyid: 9860
            propertytype: "住宅"
            registerdate: null
            signingdate: "2018-10-13 00:00:00"
            submitteddate: "2004-03-24 00:00:00"
            unitprice: 61378
            usd: 6600000
            """
            # try:
            #     data_list = com_dict['data']['sets']['items']
            #     for data in data_list:
            #         collection.insert_one(data)
            #         print('插入一条数据{}'.format(data))
            # except:
            #     continue


if __name__ == '__main__':
    a = Anyproxy()
    a.get_data()