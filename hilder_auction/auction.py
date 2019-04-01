"""
字段
"""
import datetime
import yaml
from lib.log import LogHandler
from lib.mongo import Mongo
import datetime

log = LogHandler(__name__)

setting = yaml.load(open('config.yaml'))
client = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port'], user_name=setting['mongo']['user_name'],
               password=setting['mongo']['password']).connect
coll = client[setting['mongo']['db']][setting['mongo']['collection']]
coll.create_index([('auctionId', 1), ('source', 1)],unique=True)
coll.create_index('biddingState')


def serialization_info(info):
    """
    :param info:
    :return: data:
    """
    return {key: value for key, value in vars(info).items()}


class Auction:
    def __init__(self, source, name=None, address=None, auction_name=None, start_auction_price=None, assess_value=None,
                 earnest_money=None, auction_level=None, build_type=None, info=None, auction_id=None, auction_time=None,
                 area=None, floor=None, province=None, curprice=None, stage=None, city=None, region=None, deal_price=None,
                 auction_start_time=None, total_floor=None, house_images=None, visit=0, lng=None, lat=None, partnumber=0,
                 biddingstate=None, url=None, matchCity=None, matchRegion=None, matchName=None, houseNum=None, roomNum=None,
                 sortIndex=None, followCount=None, cutCity=None, cutRegion=None, cutName=None, cutAddress=None,
                 cutHouseNum=None, matchAddress=None):
        self.auction_name = auction_name  # 拍卖物品名称
        self.city = city  # 市
        self.region = region  # 区域
        self.name = name  # 小区名称
        self.address = address  # 地址
        self.curPrice = curprice  # 当前价(万)
        self.participantsNumber = partnumber  # 参与人数
        self.startShootingDate = auction_start_time  # 拍卖开始时间
        self.endShootingDate = auction_time  # 拍卖结束时间
        self.startPrice = start_auction_price  # 起拍价(万)
        self.evalPrice = assess_value  # 评估值(万)
        self.bond = earnest_money  # 保证金(万)
        self.auctionCount = auction_level  # 拍卖次数
        self.area = area  # 面积   # todo
        self.curFloor = floor  # 当前楼层  # todo
        self.totalFloor = total_floor  # 总楼层  # todo
        self.houseImgUrls = house_images  # 房屋图片列表
        self.biddingState = biddingstate  # 竞拍状态（发布，正在开拍，已成交，缓拍，流拍，拍卖中止，撤拍）
        self.auctionStage = stage  # 拍卖阶段(一拍，二拍，三拍，重拍，变卖)
        self.dealPrice = deal_price  # 成交价格(万)
        self.visitCount = visit  # 浏览数量
        self.sortIndex = sortIndex  # 排序索引  # todo
        self.followCount = followCount  # 关注量   # todo
        self.buildType = build_type  # 房产\住宅用房  # todo
        self.info = info  # 房屋信息    # todo
        self.source = source  # 网站来源
        self.auctionId = str(auction_id)  # 拍卖物品id
        self.province = province  # 省  # todo
        self.url = url
        # 切割得到的数据
        self.cutCity = cutCity            # 城市
        self.cutRegion = cutRegion        # 区域
        self.cutName = cutName            # 小区名称
        self.cutAddress = cutAddress      # 地址
        self.cutHouseNum = cutHouseNum    # 楼号
        self.matchAddress = matchAddress  # 匹配的地址
        self.matchCity = matchCity        # 匹配城市
        self.matchRegion = matchRegion    # 匹配区域
        self.matchName = matchName        # 匹配名称
        self.houseNum = houseNum          # 楼号
        self.roomNum = roomNum            # 室号
        self.lng = lng                    # 经度
        self.lat = lat                    # 纬度

    def update(self):
        data = serialization_info(self)
        data['update_time'] = datetime.datetime.now()
        realtion = {'发布': 1, '开拍': 2, '已成交': 3, '缓拍': 4, '流拍': 5, '拍卖中止': 6, '撤拍': 7}
        if data['source'] == 'ali':
            if data['biddingState'] == '已成交':
                data['dealPrice'] = data['curPrice']
        if data['biddingState'] == '正在开拍':
            data['biddingState'] = '开拍'
        if data['auctionStage'] == '第一次拍卖':
            data['auctionStage'] = '一拍'
        if data['auctionStage'] == '第二次拍卖':
            data['auctionStage'] = '二拍'
        if data['auctionStage'] == '第三次拍卖':
            data['auctionStage'] = '三拍'
        if data['auctionStage'] == '重新拍卖' or data['auctionStage'] == '再次拍卖':
            data['auctionStage'] = '重拍'
        if data['houseNum']:
            if data['cutAddress']:
                if data['houseNum'] in data['cutAddress']:
                    data['houseNum'] = None
        data['sortIndex'] = realtion[data['biddingState']]
        coll.update_one({'source': data['source'], 'auctionId': data['auctionId']}, {'$set': data}, upsert=True)
        log.info('更新数据 ID={},更新时间={}, url={}'.format(data['auctionId'], datetime.datetime.now(), data['url']))