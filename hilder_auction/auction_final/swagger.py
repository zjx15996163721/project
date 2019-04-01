import requests
from lib.mongo import Mongo
from lib.log import LogHandler
import yaml
import json
from retry import retry

setting = yaml.load(open('config.yaml'))
m = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port'],
          user_name=setting['mongo']['user_name'], password=setting['mongo']['password']).connect
coll = m[setting['mongo']['db']][setting['mongo']['collection']]

log = LogHandler(__name__)


# todo 调用技术部的接口 每一个小时返回数据
class Swagger(object):

    def __init__(self):
        self.headers = {
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        }

    # @retry(delay=1,tries=3)
    def request(self):
        count = 0
        for info in coll.find({}, no_cursor_timeout=True):
            count += 1
            url = 'http://basicapi.fangjia.com/auction-data-service/auctionData/add'
            if info['lat'] is None:
                data = {
                    "address": info['cutAddress'],
                    "area": info['area'],
                    "auctionCount": info['auctionCount'],
                    "auctionStage": info['auctionStage'],
                    "biddingState": info['biddingState'],
                    "bond": info['bond'],
                    "city": info['cutCity'],
                    "curFloor": info['curFloor'],
                    "curPrice": info['curPrice'],
                    "dealPrice": info['dealPrice'],
                    "endShootingDate": str(info['endShootingDate']),
                    "evalPrice": info['evalPrice'],
                    "followCount": info['followCount'],
                    "hosueNum": info['houseNum'],
                    "houseImgUrls": info['houseImgUrls'],
                    "id": info['auctionId'],
                    "lat": None,
                    "lng": None,
                    "matchCity": info['matchCity'],
                    "matchName": info['matchName'],
                    "matchRegion": info['matchRegion'],
                    "name": info['auction_name'],
                    "participantsNumber": info['participantsNumber'],
                    "region": info['cutRegion'],
                    "roomNum": info['roomNum'],
                    "sortIndex": info['sortIndex'],
                    "startPrice": info['startPrice'],
                    "startShootingDate": str(info['startShootingDate']),
                    "totalFloor": info['totalFloor'],
                    "visitCount": info['visitCount']
                }
                try:
                    r = requests.post(url=url, data=json.dumps(data), headers=self.headers)
                    print(r.status_code)
                    print(count)
                except Exception as e:
                    log.error(e)
                    continue
            else:
                data = {
                    "address": info['cutAddress'],
                    "area": info['area'],
                    "auctionCount": info['auctionCount'],
                    "auctionStage": info['auctionStage'],
                    "biddingState": info['biddingState'],
                    "bond": info['bond'],
                    "city": info['cutCity'],
                    "curFloor": info['curFloor'],
                    "curPrice": info['curPrice'],
                    "dealPrice": info['dealPrice'],
                    "endShootingDate": str(info['endShootingDate']),
                    "evalPrice": info['evalPrice'],
                    "followCount": info['followCount'],
                    "hosueNum": info['houseNum'],
                    "houseImgUrls": info['houseImgUrls'],
                    "id": info['auctionId'],
                    "lat": float(info['lat']),
                    "lng": float(info['lng']),
                    "matchCity": info['matchCity'],
                    "matchName": info['matchName'],
                    "matchRegion": info['matchRegion'],
                    "name": info['auction_name'],
                    "participantsNumber": info['participantsNumber'],
                    "region": info['cutRegion'],
                    "roomNum": info['roomNum'],
                    "sortIndex": info['sortIndex'],
                    "startPrice": info['startPrice'],
                    "startShootingDate": str(info['startShootingDate']),
                    "totalFloor": info['totalFloor'],
                    "visitCount": info['visitCount']
                }
                try:
                    r = requests.post(url=url, data=json.dumps(data), headers=self.headers)
                    print(r.status_code)
                    print(count)
                except Exception as e:
                    log.error(e)
                    continue


if __name__ == '__main__':
    swagger = Swagger()
    swagger.request()
