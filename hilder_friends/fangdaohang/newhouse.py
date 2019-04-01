import requests
import json
from lib.log import LogHandler
import re
from lib.mongo import Mongo

log = LogHandler("房导航")
source = '房导航'
client = Mongo(host='114.80.150.196',port=27777, user_name='goojia',
               password='goojia7102')
collection = client.connect['friends']['fangdaohang_newhouse_1']


def build(id,index_res):
    url = 'http://114.80.150.196:8002/fetchBody?id=' + str(id)
    res = requests.get(url)
    build_dict = res.json()
    try:
        resbody = json.loads(build_dict['resBody'])
        for i in resbody['data']['items']:
            diskid = i['newdiskid']
            buildingsid = i['buildingsid']
            buildingsnum = i['floorno']
            house(diskid,buildingsid,buildingsnum,index_res)
    except:
        print("非楼栋信息")

def house(diskid,buildingsid,buildingsnum,res):
    for i in res.json():
        try:
            sid = re.search('buildid=(\d+)', i['reqBody']).group(1)
            if buildingsid == sid:
                request_id = i['id']
                url = 'http://114.80.150.196:8002/fetchBody?id=' + str(request_id)
                house_res = requests.get(url)
                resbody = json.loads(house_res.json()['resBody'])
                # for house in resbody['data']['overground']:
                #     for ho in house['layers']:
                #         ho['floor'] = house['floor']
                #         ho['diskid'] = diskid
                #         ho['buildingsid'] = buildingsid
                #         ho['buildingsnum'] = buildingsnum
                #         roomid = ho['roomid']
                #         insert(roomid,ho)
                for house in resbody['data']['underground']:
                    for ho in house['layers']:
                        ho['floor'] = house['floor']
                        ho['diskid'] = diskid
                        ho['buildingsid'] = buildingsid
                        ho['buildingsnum'] = buildingsnum
                        roomid = ho['roomid']
                        insert(roomid,ho)
        except:
            continue


def insert(roomid,data):
    collection.update_one({'roomid': roomid}, {'$set': data}, upsert=True)
    print("更新房屋id{}的数据".format(roomid))


if __name__ == '__main__':

    anyproxy = 'http://114.80.150.196:8002/latestLog'
    index_res = requests.get(anyproxy)
    for id in range(72206,80000):
        build(id,index_res)
        print('id={}'.format(id))
    # for id in range(38900,70000):
    #     comm(id)
    #     print('id={}'.format(id))