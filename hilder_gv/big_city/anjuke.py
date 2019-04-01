import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
import aiohttp
import asyncio
import threading
from lib.log import LogHandler
import time
import pika
import json
import gevent
from gevent import monkey
monkey.patch_all()
log = LogHandler('anjuke')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['anjuke']

top_city_list = ['上海', '北京', '广州', '深圳', '天津',
                 '无锡', '西安', '武汉', '大连', '宁波',
                 '南京', '沈阳', '苏州', '青岛', '长沙',
                 '成都', '重庆', '杭州', '厦门']


class AnJuKe:

    def __init__(self):
        self.headers = {
            'upgrade-insecure-requests': '1',
            'cookie': 'aQQ_ajkguid=75D77C2A-F680-B489-349F-906930217233; lps=http%3A%2F%2Fshanghai.anjuke.com%2Fcommunity%2Fpudong%2F%7C; twe=2; sessid=E18EB609-6C8E-818B-7EED-C86C2FD5AC83; 58tj_uuid=dea223f6-6b4a-48f1-92af-01ee6a85f34d; init_refer=; new_uv=1; als=0; new_session=0; _ga=GA1.2.1395916484.1545029002; _gid=GA1.2.1022907573.1545029002; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-b; ctid=46; wmda_uuid=09ced73898e209093026d9a297fe1372; wmda_new_uuid=1; wmda_session_id_6289197098934=1545033749144-6ef4fcc0-3c40-26a2; wmda_visited_projects=%3B6289197098934; __xsptplusUT_8=1; __xsptplus8=8.1.1545028464.1545033826.309%234%7C%7C%7C%7C%7C%23%23O0T93MI8LRY7Mmh5GelYb6PAJEBZE-2Y%23',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url_list = [('https://shanghai.anjuke.com/community/pudong/', 3291),
                               ('https://shanghai.anjuke.com/community/minhang/', 1480),
                               ('https://shanghai.anjuke.com/community/baoshan/', 1055),
                               ('https://shanghai.anjuke.com/community/xuhui/', 1511),
                               ('https://shanghai.anjuke.com/community/songjiang/', 1004),
                               ('https://shanghai.anjuke.com/community/jiading/', 1002),
                               ('https://shanghai.anjuke.com/community/jingan/', 1548),
                               ('https://shanghai.anjuke.com/community/putuo/', 936),
                               ('https://shanghai.anjuke.com/community/yangpu/', 1174),
                               ('https://shanghai.anjuke.com/community/hongkou/', 1076),
                               ('https://shanghai.anjuke.com/community/changning//', 1075),
                               ('https://shanghai.anjuke.com/community/huangpu/', 1144),
                               ('https://shanghai.anjuke.com/community/qingpu/', 756),
                               ('https://shanghai.anjuke.com/community/fengxian/', 579),
                               ('https://shanghai.anjuke.com/community/jinshan/', 379),
                               ('https://shanghai.anjuke.com/community/chongming/', 203),
                               ('https://shanghai.anjuke.com/community/shanghaizhoubian/', 11450),
                               ('https://beijing.anjuke.com/community/chaoyang/', 1810),
                               ('https://beijing.anjuke.com/community/haidian/', 1517),
                               ('https://beijing.anjuke.com/community/dongchenga/', 912),
                               ('https://beijing.anjuke.com/community/xicheng/', 1354),
                               ('https://beijing.anjuke.com/community/fengtai/', 1034),
                               ('https://beijing.anjuke.com/community/tongzhou/', 635),
                               ('https://beijing.anjuke.com/community/shijingshan/', 230),
                               ('https://beijing.anjuke.com/community/changping/', 675),
                               ('https://beijing.anjuke.com/community/daxing/', 538),
                               ('https://beijing.anjuke.com/community/shunyi/', 338),
                               ('https://beijing.anjuke.com/community/fangshan/', 472),
                               ('https://beijing.anjuke.com/community/mentougou/', 216),
                               ('https://beijing.anjuke.com/community/miyun/', 180),
                               ('https://beijing.anjuke.com/community/huairou/', 172),
                               ('https://beijing.anjuke.com/community/pinggua/', 120),
                               ('https://beijing.anjuke.com/community/yanqing/', 85),
                               ('https://beijing.anjuke.com/community/beijingzhoubiana/', 9424),
                               ('https://guangzhou.anjuke.com/community/fanyu/', 1042),
                                ('https://guangzhou.anjuke.com/community/tianhe/', 1312),
                                ('https://guangzhou.anjuke.com/community/baiyun/', 1044),
                                ('https://guangzhou.anjuke.com/community/haizhu/', 992),
                                ('https://guangzhou.anjuke.com/community/zengcheng/', 456),
                                ('https://guangzhou.anjuke.com/community/huadu/', 806),
                                ('https://guangzhou.anjuke.com/community/yuexiu/', 1223),
                                ('https://guangzhou.anjuke.com/community/huangpua/', 318),
                                ('https://guangzhou.anjuke.com/community/nansha/', 221),
                                ('https://guangzhou.anjuke.com/community/liwan/', 664),
                                ('https://guangzhou.anjuke.com/community/conghua/', 233),
                                ('https://guangzhou.anjuke.com/community/guangzhouzhoubian/', 8733),
                                ('https://shenzhen.anjuke.com/community/guangmingx/', 100),
                                ('https://shenzhen.anjuke.com/community/nanshan/', 940),
                                ('https://shenzhen.anjuke.com/community/futian/', 946),
                                ('https://shenzhen.anjuke.com/community/luohu/', 831),
                                ('https://shenzhen.anjuke.com/community/longgang/', 901),
                                ('https://shenzhen.anjuke.com/community/longhuaq/', 589),
                                ('https://shenzhen.anjuke.com/community/baoan/', 933),
                                ('https://shenzhen.anjuke.com/community/pingshanq/', 72),
                                ('https://shenzhen.anjuke.com/community/yantian/', 223),
                                ('https://shenzhen.anjuke.com/community/shenzhenzhoubian/', 3979),
                               ('https://tianjin.anjuke.com/community/beichenqu/', 381),
                               ('https://tianjin.anjuke.com/community/hepingc/', 484),
                               ('https://tianjin.anjuke.com/community/hexi/', 668),
                               ('https://tianjin.anjuke.com/community/baodiqu/', 162),
                               ('https://tianjin.anjuke.com/community/nankai/', 703),
                               ('https://tianjin.anjuke.com/community/jizhouqujixian/', 146),
                               ('https://tianjin.anjuke.com/community/jianghaiqujinghaixian/', 301),
                               ('https://tianjin.anjuke.com/community/ninghequninghexian/', 70),
                               ('https://tianjin.anjuke.com/community/hebei/', 493),
                               ('https://tianjin.anjuke.com/community/hedong/', 630),
                               ('https://tianjin.anjuke.com/community/hongqiaob/', 319),
                               ('https://tianjin.anjuke.com/community/binhaixinqu/', 1185),
                               ('https://tianjin.anjuke.com/community/xiqing/', 578),
                               ('https://tianjin.anjuke.com/community/jinnan/', 442),
                               ('https://tianjin.anjuke.com/community/dongli/', 473),
                               ('https://tianjin.anjuke.com/community/wuqingqu/', 462),
                               ('https://tianjin.anjuke.com/community/tianjinzhoubian/', 5139),
                               ('https://wuxi.anjuke.com/community/xinwu/', 343),
                               ('https://wuxi.anjuke.com/community/binhu/', 568),
                               ('https://wuxi.anjuke.com/community/liangxi/', 704),
                               ('https://wuxi.anjuke.com/community/huishana/', 435),
                               ('https://wuxi.anjuke.com/community/xishand/', 361),
                               ('https://wuxi.anjuke.com/community/jiangyin/', 675),
                               ('https://wuxi.anjuke.com/community/yixinga/', 516),
                               ('https://xa.anjuke.com/community/yantaqu/', 1198),
                               ('https://xa.anjuke.com/community/weiyangq/', 887),
                               ('https://xa.anjuke.com/community/changanb/', 420),
                               ('https://xa.anjuke.com/community/beilinqu/', 676),
                               ('https://xa.anjuke.com/community/lianhuqu/', 747),
                               ('https://xa.anjuke.com/community/xinchengqu/', 458),
                               ('https://xa.anjuke.com/community/baqiaoqu/', 309),
                               ('https://xa.anjuke.com/community/gaoling/', 116),
                               ('https://xa.anjuke.com/community/huyiqu/', 77),
                               ('https://xa.anjuke.com/community/lintongqu/', 87),
                               ('https://xa.anjuke.com/community/lantianxian/', 9),
                               ('https://xa.anjuke.com/community/yanliangqu/', 31),
                               ('https://xa.anjuke.com/community/zhouzhixian/', 20),
                               ('https://xa.anjuke.com/community/xianzhoubianc/', 875),
                               ('https://wuhan.anjuke.com/community/wuchanga/', 917),
                               ('https://wuhan.anjuke.com/community/hongshana/', 861),
                               ('https://wuhan.anjuke.com/community/jiangan/', 839),
                               ('https://wuhan.anjuke.com/community/hanyang/', 506),
                               ('https://wuhan.anjuke.com/community/jianghana/', 530),
                               ('https://wuhan.anjuke.com/community/qiaokou/', 438),
                               ('https://wuhan.anjuke.com/community/dongxihu/', 346),
                               ('https://wuhan.anjuke.com/community/jiangxiat/', 414),
                               ('https://wuhan.anjuke.com/community/huangpiz/', 315),
                               ('https://wuhan.anjuke.com/community/qingshan/', 231),
                               ('https://wuhan.anjuke.com/community/caidianz/', 391),
                               ('https://wuhan.anjuke.com/community/xinzhouz/', 199),
                               ('https://wuhan.anjuke.com/community/hannanz/', 66),
                               ('https://dalian.anjuke.com/community/zhongshane/', 435),
                               ('https://dalian.anjuke.com/community/xigang/', 294),
                               ('https://dalian.anjuke.com/community/shahekou/', 470),
                               ('https://dalian.anjuke.com/community/ganjingzi/', 774),
                               ('https://dalian.anjuke.com/community/jinzhou/', 675),
                               ('https://dalian.anjuke.com/community/lvshunkou/', 236),
                               ('https://dalian.anjuke.com/community/wafangdiana/', 206),
                               ('https://dalian.anjuke.com/community/pulandiana/', 134),
                               ('https://dalian.anjuke.com/community/zhuanghea/', 130),
                               ('https://dalian.anjuke.com/community/changhai/', 4),
                               ('https://nb.anjuke.com/community/yinzhou/', 1028),
                               ('https://nb.anjuke.com/community/haishu/', 788),
                               ('https://nb.anjuke.com/community/yuyao/', 288),
                               ('https://nb.anjuke.com/community/jiangbeia/', 277),
                               ('https://nb.anjuke.com/community/cixi/', 332),
                               ('https://nb.anjuke.com/community/beilun/', 364),
                               ('https://nb.anjuke.com/community/zhenhai/', 261),
                               ('https://nb.anjuke.com/community/xiangshana/', 179),
                               ('https://nb.anjuke.com/community/ninghaia/', 99),
                               ('https://nb.anjuke.com/community/fenghuab/', 152),
                               ('https://nanjing.anjuke.com/community/jiangninga/', 876),
                               ('https://nanjing.anjuke.com/community/pukou/', 401),
                               ('https://nanjing.anjuke.com/community/jianye/', 403),
                               ('https://nanjing.anjuke.com/community/guloua/', 1240),
                               ('https://nanjing.anjuke.com/community/qinhuai/', 959),
                               ('https://nanjing.anjuke.com/community/xuanwub/', 578),
                               ('https://nanjing.anjuke.com/community/qixia/', 423),
                               ('https://nanjing.anjuke.com/community/yuhuatai/', 343),
                               ('https://nanjing.anjuke.com/community/liuhe/', 405),
                               ('https://nanjing.anjuke.com/community/lishuia/', 183),
                               ('https://nanjing.anjuke.com/community/gaochun/', 175),
                               ('https://nanjing.anjuke.com/community/nanjingzhoubian/', 1723),
                               ('https://sy.anjuke.com/community/hepingqu/', 465),
                               ('https://sy.anjuke.com/community/shenhequ/', 502),
                               ('https://sy.anjuke.com/community/dadongqu/', 368),
                               ('https://sy.anjuke.com/community/tiexiqu/', 787),
                               ('https://sy.anjuke.com/community/huangguqu/', 491),
                               ('https://sy.anjuke.com/community/hunnanxinqu/', 405),
                               ('https://sy.anjuke.com/community/yuhongqu/', 436),
                               ('https://sy.anjuke.com/community/shenbeixinqu/', 229),
                               ('https://sy.anjuke.com/community/sujiatun/', 147),
                               ('https://sy.anjuke.com/community/xinmin/', 73),
                               ('https://sy.anjuke.com/community/liaozhong/', 94),
                               ('https://sy.anjuke.com/community/faku/', 34),
                               ('https://sy.anjuke.com/community/kangping/', 20),
                               ('https://sy.anjuke.com/community/shenyangzhoubians/', 331),
                               ('https://suzhou.anjuke.com/community/wuzhong/', 3152),
                               ('https://suzhou.anjuke.com/community/xiangcheng/', 431),
                               ('https://suzhou.anjuke.com/community/wujiang/', 684),
                               ('https://suzhou.anjuke.com/community/gushuqu/', 1077),
                               ('https://suzhou.anjuke.com/community/changshua/', 706),
                               ('https://suzhou.anjuke.com/community/zhangjiagang/', 625),
                               ('https://suzhou.anjuke.com/community/huqius/', 390),
                               ('https://suzhou.anjuke.com/community/taicang/', 441),
                               ('https://qd.anjuke.com/community/huangdaoqu/', 992),
                               ('https://qd.anjuke.com/community/chengyangqu/', 550),
                               ('https://qd.anjuke.com/community/licangqu/', 389),
                               ('https://qd.anjuke.com/community/shibeiqu/', 820),
                               ('https://qd.anjuke.com/community/shinanqu/', 498),
                               ('https://qd.anjuke.com/community/laoshanqu/', 336),
                               ('https://qd.anjuke.com/community/jimoshi/', 449),
                               ('https://qd.anjuke.com/community/jiaozhoushi/', 528),
                               ('https://qd.anjuke.com/community/pingdushi/', 226),
                               ('https://qd.anjuke.com/community/laixishi/', 239),
                               ('https://qd.anjuke.com/community/qingdaozhoubian/', 1726),
                               ('https://cs.anjuke.com/community/xingsha/', 307),
                               ('https://cs.anjuke.com/community/yuelu/', 688),
                               ('https://cs.anjuke.com/community/kaifu/', 511),
                               ('https://cs.anjuke.com/community/liuyang/', 185),
                               ('https://cs.anjuke.com/community/ningxiang/', 184),
                               ('https://cs.anjuke.com/community/tianxin/', 576),
                               ('https://cs.anjuke.com/community/wangchenga/', 203),
                               ('https://cs.anjuke.com/community/yuhuah/', 944),
                               ('https://cs.anjuke.com/community/furong/', 517),
                               ('https://chengdu.anjuke.com/community/qingyang/', 1284),
                               ('https://chengdu.anjuke.com/community/jinjiang/', 947),
                               ('https://chengdu.anjuke.com/community/jinniu/', 1397),
                               ('https://chengdu.anjuke.com/community/wuhou/', 1362),
                               ('https://chengdu.anjuke.com/community/chenghua/', 1022),
                               ('https://chengdu.anjuke.com/community/gaoxin/', 728),
                               ('https://chengdu.anjuke.com/community/tainfuxinqu/', 375),
                               ('https://chengdu.anjuke.com/community/wenjiang/', 516),
                               ('https://chengdu.anjuke.com/community/longquanyi/', 532),
                               ('https://chengdu.anjuke.com/community/shuangliu/', 595),
                               ('https://chengdu.anjuke.com/community/dujiangyan/', 524),
                               ('https://chengdu.anjuke.com/community/piduqu/', 729),
                               ('https://chengdu.anjuke.com/community/xindu/', 683),
                               ('https://chengdu.anjuke.com/community/qingbaijiangqu/', 199),
                               ('https://chengdu.anjuke.com/community/xinjinxian/', 161),
                               ('https://chengdu.anjuke.com/community/jintangxian/', 210),
                               ('https://chengdu.anjuke.com/community/pengzhoushi/', 179),
                               ('https://chengdu.anjuke.com/community/chongzhoushi/', 205),
                               ('https://chengdu.anjuke.com/community/dayixian/', 156),
                               ('https://chengdu.anjuke.com/community/qionglaishi/', 173),
                               ('https://chengdu.anjuke.com/community/cdpujiangxian/', 50),
                               ('https://chengdu.anjuke.com/community/jianyangsh/', 104),
                               ('https://chengdu.anjuke.com/community/chengduzhoubian/', 119),
                               ('https://chongqing.anjuke.com/community/yubei/', 1404),
                               ('https://chongqing.anjuke.com/community/nanana/', 739),
                               ('https://chongqing.anjuke.com/community/jiangbei/', 598),
                               ('https://chongqing.anjuke.com/community/jiulongpo/', 863),
                               ('https://chongqing.anjuke.com/community/shapingba/', 685),
                               ('https://chongqing.anjuke.com/community/yuzhong/', 490),
                               ('https://chongqing.anjuke.com/community/banan/', 448),
                               ('https://chongqing.anjuke.com/community/dadukou/', 200),
                               ('https://chongqing.anjuke.com/community/beibei/', 419),
                               ('https://chongqing.anjuke.com/community/bishanqu/', 239),
                               ('https://chongqing.anjuke.com/community/hechuanqu/', 299),
                               ('https://chongqing.anjuke.com/community/yongchuanqu/', 255),
                               ('https://chongqing.anjuke.com/community/jiangjinqu/', 277),
                               ('https://chongqing.anjuke.com/community/fulingqu/', 334),
                               ('https://chongqing.anjuke.com/community/changshouqu/', 183),
                               ('https://chongqing.anjuke.com/community/wanzhouqu/', 418),
                               ('https://chongqing.anjuke.com/community/rongchangqu/', 180),
                               ('https://chongqing.anjuke.com/community/tongliangqu/', 172),
                               ('https://chongqing.anjuke.com/community/qijiangqu/', 163),
                               ('https://chongqing.anjuke.com/community/kaizhouqukaixian/', 252),
                               ('https://chongqing.anjuke.com/community/nanchuanqu/', 107),
                               ('https://chongqing.anjuke.com/community/wulongxian/', 38),
                               ('https://chongqing.anjuke.com/community/dazhuqu/', 149),
                               ('https://chongqing.anjuke.com/community/zhongxian/', 38),
                               ('https://chongqing.anjuke.com/community/shizhutujiazuzizhixian/', 21),
                               ('https://chongqing.anjuke.com/community/dainjiangxian/', 101),
                               ('https://chongqing.anjuke.com/community/tongnanqu/', 90),
                               ('https://chongqing.anjuke.com/community/fengjiexian/', 25),
                               ('https://chongqing.anjuke.com/community/fengduxian/', 21),
                               ('https://chongqing.anjuke.com/community/liangpingxian/', 54),
                               ('https://chongqing.anjuke.com/community/yunyangxian/', 24),
                               ('https://chongqing.anjuke.com/community/xiushantujiazumiaozuzizhixian/', 27),
                               ('https://chongqing.anjuke.com/community/youyangtujiazumiaozuzizhixian/', 19),
                               ('https://chongqing.anjuke.com/community/qianjiangqu/', 30),
                               ('https://chongqing.anjuke.com/community/pengshuimiaozutujiazuzizhixian/', 28),
                               ('https://chongqing.anjuke.com/community/chengkouxian/', 4),
                               ('https://chongqing.anjuke.com/community/cqwushanxian/', 20),
                               ('https://chongqing.anjuke.com/community/wuxixian/', 3),
                               ('https://hangzhou.anjuke.com/community/xiaoshan/', 721),
                               ('https://hangzhou.anjuke.com/community/binjiangb/', 227),
                               ('https://hangzhou.anjuke.com/community/xihu/', 701),
                               ('https://hangzhou.anjuke.com/community/linanq/', 310),
                               ('https://hangzhou.anjuke.com/community/yuhang/', 1015),
                               ('https://hangzhou.anjuke.com/community/jianggan/', 650),
                               ('https://hangzhou.anjuke.com/community/gongshu/', 419),
                               ('https://hangzhou.anjuke.com/community/shangcheng/', 413),
                               ('https://hangzhou.anjuke.com/community/fuyang/', 235),
                               ('https://hangzhou.anjuke.com/community/xiacheng/', 492),
                               ('https://hangzhou.anjuke.com/community/tonglu/', 232),
                               ('https://hangzhou.anjuke.com/community/chunan/', 135),
                               ('https://hangzhou.anjuke.com/community/jiande/', 122),
                               ('https://hangzhou.anjuke.com/community/hangzhouzhoubian/', 4691),
                               ('https://xm.anjuke.com/community/siming/', 1236),
                               ('https://xm.anjuke.com/community/huli/', 550),
                               ('https://xm.anjuke.com/community/haicang/', 194),
                               ('https://xm.anjuke.com/community/jimei/', 302),
                               ('https://xm.anjuke.com/community/tongana/', 261),
                               ('https://xm.anjuke.com/community/xiangana/', 108),
                               ('https://xm.anjuke.com/community/xiamenzhoubian/', 2948),
                               ]
        self.url_list = []
        self.info_list = []

    def start_crawler(self):
        for start_url in self.start_url_list:
            max_page = int(start_url[1]/30) + 1
            for page in range(1, max_page+1):
                url = start_url[0] + 'p{}/'.format(str(page))
                if len(self.url_list) == 50:
                    self.run()
                    self.url_list.clear()
                    continue
                else:
                    self.url_list.append(url)

    def run(self):
        # try:
            # loop = asyncio.get_event_loop()
            # tasks = [self.start_request(url) for url in self.url_list]
            # loop.run_until_complete(asyncio.wait(tasks))
        # except Exception as e:
        #     log.error(e)
        # for i in self.url_list:
        #     threading.Thread(target=self.start_request, args=(i,)).start()
        jobs = [gevent.spawn(self.start_request, url) for url in self.url_list]
        gevent.wait(jobs)

    # async def start_request(self, url):
    #     try:
    #
    #         await self.get_all_link(await self.url_request(url))
    #     except Exception as e:
    #         log.error(e)

    # async def url_request(self, url):
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url=url, headers=self.headers, proxy='http://FANGJIAHTT7:HGhyd7BF@http-proxy-sg2.dobel.cn:9180') as response:
    #             if response.status == 200:
    #                 con = await response.text(encoding='utf-8')
    #                 return con
    #             else:
    #                 log.error('url={}'.format(url))

    def start_request(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            return
        response = r.text
        self.get_all_link(response)

    def get_all_link(self, response):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        channel = connection.channel()
        tree = etree.HTML(response)
        detail_info_list = tree.xpath('//*[@id="list-content"]/div[@class="li-itemmod"]')
        for detail_info in detail_info_list:
            detail_url = detail_info.xpath('./div[1]/h3/a/@href')[0]
            name = detail_info.xpath('./div[1]/h3/a/text()')[0]
            data = {
                'url': detail_url,
                'name': name
            }
            channel.queue_declare(queue='anjuke')
            channel.basic_publish(exchange='',
                                  routing_key='anjuke',
                                  body=json.dumps(data))
            log.info('放队列 {}'.format(data))


if __name__ == '__main__':
    anjuke = AnJuKe()
    anjuke.start_crawler()

