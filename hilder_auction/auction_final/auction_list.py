import requests
import math
from lib.log import LogHandler
import yaml
from pymongo import MongoClient
from auction_final.jingdong import Parse
import datetime

log = LogHandler(__name__)

setting = yaml.load(open('config.yaml'))
mongo_config = setting['mongo']
client = MongoClient(host=mongo_config['host'],
                     port=mongo_config['port'],
                     username=mongo_config['user_name'],
                     password=mongo_config['password'])
coll = client[mongo_config['db']][mongo_config['collection']]


class AliList:
    def __init__(self):
        self.source = 'ali'

    def start_crawler(self):
        log.info('开始阿里拍卖抓取')
        pass


class Gdlist:
    def __init__(self):
        self.source = 'jingdong'
        # 28住宅, 09商业用房, 17工业用房, 10其他用房
        self.auction_type_list = ['13809', '13810', '13817', '12728']
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        }
        self.auction_status_list = ['0', '1', '2', '5', '6', '7']

    def start_crawler(self):
        for auction_type in self.auction_type_list:
            page_num = self.get_page(auction_type)
            for page in range(1, int(page_num) + 1):
                for auction_status_flag in self.auction_status_list:
                    url = 'http://auction.jd.com/getJudicatureList.html?page=' + str(
                        page) + '&limit=40&provinceId=2&childrenCateId=' + auction_type + '&paimaiStatus=' + auction_status_flag
                    try:
                        res = requests.get(url=url, headers=self.headers)
                        html = res.json()
                    except Exception as e:
                        log.error("列表页请求失败url={}".format(url))
                        continue
                    if auction_status_flag == '0':
                        auction_status = '发布'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])
                    elif auction_status_flag == '1':
                        auction_status = '开拍'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])
                    elif auction_status_flag == '2':
                        auction_status = '已成交'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])
                    elif auction_status_flag == '5':
                        auction_status = '撤拍'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])
                    elif auction_status_flag == '6':
                        auction_status = '缓拍'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])
                    elif auction_status_flag == '7':
                        auction_status = '拍卖中止'
                        for info in html['ls']:
                            auction_id = str(info['id'])  # 商品id
                            self.check(auction_id=auction_id,
                                       source=self.source,
                                       auction_status=auction_status,
                                       curPrice=info['currentPrice'])

    def get_page(self, type_num):
        # 上海 provinceId = 2
        url_page = 'http://auction.jd.com/getJudicatureList.html?page=1&limit=40&provinceId=2&childrenCateId=' + str(
            type_num)
        response = requests.get(url=url_page, headers=self.headers)
        number = response.json()['total']
        page_num = math.ceil(int(number) / 40)
        return page_num

    def check(self, auction_id, source, auction_status, curPrice):
        """
        todo 查询数据库，id和source是否存在，不存在调用接口
        todo 如果存在，判断auction状态是否变更，如果不更，更新列表页面数据，如果变，更新详情页数据
        :return:
        """
        result = coll.find_one({'auctionId': auction_id, 'source': source})
        if not result:
            p = Parse()
            p.get_detail(source=source, auction_id=auction_id, auction_status=auction_status)
        else:
            if result['biddingState'] == auction_status:
                # todo 调用更新列表页数据
                curPrice = float(curPrice) / 10000
                update_time = datetime.datetime.now()
                coll.update_one({'auctionId': auction_id, 'source': source}, {'$set': {'curPrice': curPrice, 'update_time': update_time}})
                log.info('更新一条数据的当前价格 curPrice={} 更新时间={}'.format(curPrice, update_time))
            else:
                p = Parse()
                p.get_detail(source=source, auction_id=auction_id, auction_status=auction_status)
