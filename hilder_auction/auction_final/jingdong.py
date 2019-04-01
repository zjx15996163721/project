"""
京东详情解析
"""
from lxml import etree
import re
import requests
import datetime
from auction_final.qiniu_fetch import qiniufetch
from auction import Auction
from lib.log import LogHandler
from auction_final.cut_match import CutMatch

log = LogHandler(__name__)


class Parse(object):

    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        }

    def request_url(self, auction_id):
        url = 'https://paimai.jd.com/{}'.format(auction_id)
        print(url)
        try:
            response = requests.get(url=url, headers=self.headers)
            return response, url
        except Exception as e:
            log.error('请求失败 url={} error={}'.format(url, e))
            return None, url

    def get_detail(self, source, auction_id, auction_status):
        response, url = self.request_url(auction_id)
        try:
            tree = etree.HTML(response.text)
            html = response.text
            auction = Auction(source=source)
            auction.url = url
            # 起拍价(万)
            startPrice = self.get_startPrice(html=html)
            startPrice = float(startPrice.replace(' ', '').replace(',', '')) / 10000
            auction.startPrice = startPrice
            # 评估价(万)
            evalPrice = self.get_evalPrice(tree=tree)
            evalPrice = float(evalPrice.replace(' ', '').replace('¥', '').replace(',', '')) / 10000
            auction.evalPrice = evalPrice
            # 保证金(万)
            bond = tree.xpath('//div[@id="content"]/div/div[2]/div[1]/div/div[2]/div[10]/ul[3]/li/span[2]/text()')[0]
            bond = bond.replace(' ', '').replace('¥', '').split('.')[0]
            bond = float(bond) / 10000
            auction.bond = bond
            # 拍卖阶段
            auctionStage_info = tree.xpath('//div[@id="content"]/div[1]/div[2]/div[1]/div[1]/div[2]/h1/text()')[0]
            auctionStage_info = auctionStage_info.replace(' ', '').replace('\n', '').replace('\t', '')
            auctionStage = auctionStage_info.split('】')[0].split('【')[1]
            auction.auctionStage = auctionStage
            # 拍卖次数
            auctionCount = self.get_auctionCount(auctionStage)
            auction.auctionCount = auctionCount
            # 拍卖物品名称
            auction_name = tree.xpath('//div[@id="content"]/div[1]/div[2]/div[1]/div[1]/div[2]/h1/text()')[0]
            auction_name = auction_name.replace(' ', '').replace('\n', '').replace('\t', '').split('】')[1]
            auction.auction_name = auction_name
            # todo 调用黄村粮的方法进行切割获取城市，区域，小区名，经纬度等
            cut_info = CutMatch.to_match('上海', auction_name)
            # 切割后匹配库中的城市
            auction.matchCity = cut_info['matchCity']
            # 切割后匹配库中的区域
            auction.matchRegion = cut_info['matchRegion']
            # 切割后匹配库中的小区名称
            auction.matchName = cut_info['matchName']
            # 切割后匹配库中的地址
            auction.matchAddress = cut_info['matchAddress']
            # 切割后的房号
            auction.roomNum = cut_info['cutRoomnum']
            # 切割后的楼号
            auction.houseNum = cut_info['cutHousenum']
            # 切割后的城市
            auction.cutCity = cut_info['cutCity']
            # 切割后的区域
            auction.cutRegion = cut_info['cutRegion']
            # 切割后的小区名称
            auction.cutName = cut_info['cutName']
            # 切割后的地址
            auction.cutAddress = cut_info['cutAddress']
            # 切割后跑高德接口得到的经纬度
            auction.lat = cut_info['mapLat']
            auction.lng = cut_info['mapLng']
            # 地址
            address = tree.xpath('//em[@id="paimaiAddress"]/text()')[0]
            auction.address = address
            # 城市
            city = address.split(' ')[0]
            auction.city = city
            # 区域
            region = address.split(' ')[1]
            auction.region = region
            skulid = re.search('id="skuId" value="(.*?)"', html, re.S | re.M).group(1)
            # 竞拍状态  当前价格  成交价格
            curPrice, dealPrice = self.get_curPrice_and_dealPrice(skulid, auction_id)
            auction.biddingState = auction_status
            auction.curPrice = curPrice
            auction.dealPrice = dealPrice
            # 起始时间
            startShootingDate = tree.xpath('//input[@id="startTime"]/@value')[0]
            startShootingDate = datetime.datetime.strptime(startShootingDate, '%Y-%m-%d %H:%M:%S.%f')
            auction.startShootingDate = startShootingDate
            # 结束时间
            endShootingDate = tree.xpath('//input[@id="endTime"]/@value')[0]
            endShootingDate = datetime.datetime.strptime(endShootingDate, '%Y-%m-%d %H:%M:%S.%f')
            auction.endShootingDate = endShootingDate
            # 图片
            houseImgUrls = []
            houseImgUrls_info = tree.xpath('//div[@id="spec-list"]/div/ul/li/img/@src')
            for houseImgUrl in houseImgUrls_info:
                houseImgUrl = 'http:' + houseImgUrl
                big_img = houseImgUrl.replace('jfs','s1000x750_jfs')
                new_houseImgUrl = qiniufetch(big_img, big_img)
                houseImgUrls.append(new_houseImgUrl)
            auction.houseImgUrls = houseImgUrls
            # 参与人数 浏览数量
            participantsNumber, visitCount = self.get_participantsNumber_and_visitCount(auction_id)
            auction.participantsNumber = participantsNumber
            auction.visitCount = visitCount
            # 拍卖物品id
            auction.auctionId = auction_id
            # 网站来源(jingdong)
            auction.source = source
            auction.update()
        except Exception as e:
            log.error('解析错误')

    def get_startPrice(self, html):
        try:
            startPrice = re.search('起拍价：.*?<em.*?>&yen;(.*?)</em>', html, re.S | re.M).group(1)
            return startPrice
        except:
            startPrice = re.search('变卖价：.*?<em.*?>&yen;(.*?)</em>', html, re.S | re.M).group(1)
            return startPrice

    def get_evalPrice(self, tree):
        try:
            evalPrice = tree.xpath('//div[@id="content"]/div/div[2]/div[1]/div/div[2]/div[10]/ul[2]/li[3]/em/text()')[0]
            return evalPrice
        except:
            evalPrice = tree.xpath('//div[@id="content"]/div/div[2]/div[1]/div/div[2]/div[10]/ul[3]/li[2]/em/text()')[0]
            return evalPrice

    def get_auctionCount(self, auctionStage):
        try:
            auctionCount = re.search('第(.*?)次', auctionStage, re.S | re.M).group(1)
            return auctionCount
        except:
            return None

    def get_participantsNumber_and_visitCount(self, auction_id):      # 参与人数 浏览数量
        url = 'https://paimai.jd.com/json/ensure/queryAccess?paimaiId={}'.format(auction_id)
        try:
            res = requests.get(url=url, headers=self.headers)
            return res.json()['accessEnsureNum'], res.json()['accessNum']
        except Exception as e:
            log.error('请求失败 url={} error={}'.format(url, e))
            return None, None

    def get_curPrice_and_dealPrice(self, skulid, auction_id):
        url = 'http://paimai.jd.com/json/current/englishquery.html?paimaiId={}&skuId={}&start=0&end=9'.format(auction_id, skulid)
        res = requests.get(url=url, headers=self.headers)
        if res.json()['auctionStatus'] == '0':        # 状态为0 表示预告中
            curPrice = res.json()['currentPrice']
            curPrice = float(curPrice) / 10000
            dealPrice = None
            return curPrice, dealPrice
        elif res.json()['auctionStatus'] == '1':      # 状态为1 表示拍卖中
            curPrice = res.json()['currentPrice']
            curPrice = float(curPrice) / 10000
            dealPrice = None
            return curPrice, dealPrice
        elif res.json()['auctionStatus'] == '2':      # 状态为2 表示已结束等
            curPrice = None
            dealPrice = res.json()['currentPrice']
            dealPrice = float(dealPrice) / 10000
            return curPrice, dealPrice


