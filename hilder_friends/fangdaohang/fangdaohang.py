import requests
import json
from lib.log import LogHandler
import re
import time
import datetime
from pymongo import MongoClient
from lib.mongo import Mongo

log = LogHandler("房导航")
source = '房导航'
client = Mongo(host='114.80.150.196',port=27777, user_name='goojia',
               password='goojia7102')
collection = client.connect['friends']['fangdaohang']

class Fangdaohang:
    def __init__(self):
        self.anyproxy = "http://114.80.150.196:8002/latestLog"

    def get_comminfo(self):
        res = requests.get(self.anyproxy)
        res_list = json.loads(res.text)
        for id in range(1,40000):
                url = 'http://localhost:8002/fetchBody?id=' + str(id)
                comm_res = requests.get(url)
                com_dict = json.loads(comm_res.text)
                try:
                    data = com_dict['resBody']
                    m = json.loads(data)
                    area = m['data']['area']
                    com_name = m['data']['newdiskname']
                    co_name = re.search('(.*?)\d+',com_name).group(1)
                    address = m['data']['address']
                    build_end_time = m['data']['completeddate']
                    bargain_avgprice = m['data']['bargainavgprice']
                    build_size = m['data']['builtuparea']
                    volumetric = m['data']['plotratio']
                    green = m['data']['greeningrate']
                    developers = m['data']['developers']
                    parking_place = m['data']['parkingspace']
                    property_cost = m['data']['propertyfee']
                    households = m['data']['totalhouseholds']
                    avg_price = m['data']['avgprice']
                    updatetime = datetime.datetime.now()
                    data = {"area":area,"co_name":co_name,"address":address,"build_en_time":build_end_time,
                            "bargain_avgprice":bargain_avgprice,"build_size":build_size,"volumetric":volumetric,
                            "greenrate":green,"developers":developers,"parking_place":parking_place,"propertyfee":property_cost,
                            "households":households,"avgprice":avg_price,'updatetime':updatetime}
                    collection.update_one({'co_name':co_name,'area':area},{'$set':data},upsert=True)
                    log.info("更新数据{}".format(co_name))
                except:
                    continue



if __name__ == '__main__':
    fang = Fangdaohang()
    fang.get_comminfo()