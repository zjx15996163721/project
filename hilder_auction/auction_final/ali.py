import re
import json
import time
from lxml import etree
import requests
import yaml
from lib.mongo import Mongo
from lib.log import LogHandler
from auction import Auction
from auction_final.qiniu_fetch import qiniufetch
import datetime
from auction_final.cut_match import CutMatch

setting = yaml.load(open('config.yaml'))
m = Mongo(host=setting['mongo']['host'], port=setting['mongo']['port'],
          user_name=setting['mongo']['user_name'], password=setting['mongo']['password']).connect
coll = m[setting['mongo']['db']][setting['mongo']['collection']]

log = LogHandler(__name__)


class Ali:
    def __init__(self):
        self.start_url = 'http://sf.taobao.com/list/50025969_____%C9%CF%BA%A3.htm?spm=a213w.7398504.pagination.3.176412d9Nz4DtZ&auction_start_seg=-1'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                                    (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        self.status_realtion = {'doing': '开拍', 'todo': '发布', 'done': '已成交', 'break': '拍卖中止', 'revocation': '撤拍', 'failure': '流拍'}

    def start_crawler(self):
        res = requests.get(self.start_url, headers=self.headers)
        page = re.search('共<em class="page-total">(\d+)</em>页', res.content.decode('gbk')).group(1)
        for i in range(1, int(page) + 1):
            url = self.start_url + "&page={}".format(i)
            page_res = requests.get(url, headers=self.headers)
            html = etree.HTML(page_res.content.decode('gbk'))
            text = html.xpath('//script[@id="sf-item-list-data"]/text()')[0]
            auction_info = json.loads(text)
            for info in auction_info['data']:
                auction_id = info['id']
                auction_status = self.status_realtion[info['status']]
                auction_name = info['title']
                currentPrice = float(info['currentPrice'])/10000.0
                evalprice = float(info['consultPrice'])/10000.0
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(info['start']) / 1000.0))
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(info['end']) / 1000.0))
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                partnumber = info['applyCount']
                visitCount = info['viewerCount']
                url = 'http:' + info['itemUrl']
                if coll.find_one({'source': 'ali', 'auctionId': auction_id, 'biddingState': auction_status}):
                    coll.update_one({'auctionId': auction_id, 'source': 'ali'}, {'$set': {'auction_name': auction_name,
                                                                                          'curPrice': currentPrice,
                                                                                          'evalPrice': evalprice,
                                                                                          'startShootingDate': start_time,
                                                                                          'endShootingDate': end_time,
                                                                                          'participantsNumber': partnumber,
                                                                                          'visitCount': visitCount,
                                                                                          'update_time': datetime.datetime.now()}})
                    log.info('更新一条数据 ID={}, 更新时间={}, url={}'.format(auction_id, datetime.datetime.now(), url))
                else:
                    self.detail_parse(auction_name=auction_name, auction_id=auction_id, status=auction_status,
                                      current_price=currentPrice, evalprice=evalprice, start_time=start_time,
                                      end_time=end_time, partnumber=partnumber, visitCount=visitCount, url=url)

    def detail_parse(self, **kwargs):
        auction = Auction(source='ali')
        auction.auction_name = kwargs['auction_name']
        auction.auctionId = kwargs['auction_id']
        auction.biddingState = kwargs['status']
        auction.curPrice = kwargs['current_price']
        auction.evalPrice = kwargs['evalprice']
        auction.startShootingDate = kwargs['start_time']
        auction.endShootingDate = kwargs['end_time']
        auction.participantsNumber = kwargs['partnumber']
        auction.visitCount = kwargs['visitCount']
        detail_url = kwargs['url']
        auction.url = detail_url
        try:
            # todo 调用黄村粮的方法进行切割获取城市，区域，小区名，经纬度等
            cut_info = CutMatch.to_match('上海', kwargs['auction_name'])
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
        except Exception as e:
            log.error(e)
            return
        try:
            detail_res = requests.get(url=detail_url, headers=self.headers)
        except Exception as e:
            log.error('url={}, e={}'.format(detail_url, e))
            return
        html = etree.HTML(detail_res.content.decode('gbk'))
        try:
            title = html.xpath('//div[contains(@class,"pm-main clearfix")]/h1/text()')[0].strip()
        except:
            log.error('没有标题 url={}'.format(detail_url))
            return
        auctionStage = re.search('【(.*?)】', title).group(1)
        auction.auctionStage = auctionStage
        auction.auctionCount = self.get_auctionCount(auctionStage)
        startPrice = re.search('起拍价￥(.*?) ，', detail_res.content.decode('gbk')).group(1)
        bond = re.search('保 证 金.*?J_Price">(.*?)</span', detail_res.content.decode('gbk'), re.S | re.M).group(1)
        comm_url = 'http://sf.taobao.com/json/getGovItemSummary.htm?itemId={}'.format(kwargs['auction_id'])
        res = requests.get(comm_url, headers=self.headers)
        try:
            auction.area = float(int(res.json()['props']['area']['value']) / 100)
        except:
            pass
        images = html.xpath("//div[@class='pm-pic pm-s80 ']/a/img/@src")
        image_list = []
        for image_url in images:
            big_img = image_url.replace('_80x80.jpg','')
            image = qiniufetch(big_img, big_img)
            image_list.append(image)
        auction.houseImgUrls = image_list
        auction.startPrice = float(float(startPrice.replace(',', '')) / 10000)
        auction.bond = float(float(bond.replace(',', '').strip()) / 10000)
        if kwargs['status'] == '已成交':
            if re.search('失败|流拍', html.xpath('//h1[@class="bid-fail"]/text()')[0]) is None:
                auction.update()
            else:
                auction.biddingState = '流拍'
                auction.update()
        else:
            auction.update()

    def get_auctionCount(self, auctionStage):
        try:
            auctionCount = re.search('第(.*?)次', auctionStage, re.S | re.M).group(1)
            return auctionCount
        except:
            return None
