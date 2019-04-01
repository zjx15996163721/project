from gevent import monkey

monkey.patch_all()
import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
from lib.log import LogHandler
import pika
import json
from retry import retry
import gevent

log = LogHandler('anjuke_producer')
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['sichuan']
sichuan_city_list = ['成都', '绵阳', '宜宾', '自贡', '攀枝花',
                     '广元', '乐山', '南充', '泸州', '资阳',
                     '内江', '达州', '巴中', '遂宁', '眉山',
                     '德阳', '广安', '雅安', '阿坝州', '甘孜州', '凉山州']


class AnJuKe:

    def __init__(self):
        self.headers = {
            'upgrade-insecure-requests': '1',
            'cookie': 'aQQ_ajkguid=75D77C2A-F680-B489-349F-906930217233; lps=http%3A%2F%2Fshanghai.anjuke.com%2Fcommunity%2Fpudong%2F%7C; twe=2; sessid=E18EB609-6C8E-818B-7EED-C86C2FD5AC83; 58tj_uuid=dea223f6-6b4a-48f1-92af-01ee6a85f34d; init_refer=; new_uv=1; als=0; new_session=0; _ga=GA1.2.1395916484.1545029002; _gid=GA1.2.1022907573.1545029002; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-b; ctid=46; wmda_uuid=09ced73898e209093026d9a297fe1372; wmda_new_uuid=1; wmda_session_id_6289197098934=1545033749144-6ef4fcc0-3c40-26a2; wmda_visited_projects=%3B6289197098934; __xsptplusUT_8=1; __xsptplus8=8.1.1545028464.1545033826.309%234%7C%7C%7C%7C%7C%23%23O0T93MI8LRY7Mmh5GelYb6PAJEBZE-2Y%23',
            # 'cookie': 'aQQ_ajkguid=3B925B01-F50E-3CDC-7029-00223852FEC0; expires=Fri, 27-Dec-2019 07:53:10 GMT; Max-Age=31622400; path=/; domain=.anjuke.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url_list = [('https://neijiang.anjuke.com/community/dongxingb/', 184),
                               ('https://neijiang.anjuke.com/community/shizhongquabc/', 138),
                               ('https://neijiang.anjuke.com/community/weiyuanb/', 73),
                               ('https://neijiang.anjuke.com/community/zizhongb/', 62),
                               ('https://neijiang.anjuke.com/community/longchangb/', 107),
                               ('https://dazhou.anjuke.com/community/tongchuan/',248),
                               ('https://dazhou.anjuke.com/community/daxianb/', 150),
                               ('https://dazhou.anjuke.com/community/xuanhanb/', 8),
                               ('https://dazhou.anjuke.com/community/kaijiangb/', 1),
                               ('https://dazhou.anjuke.com/community/dazhu/', 113),
                               ('https://dazhou.anjuke.com/community/quxian/', 58),
                               ('https://dazhou.anjuke.com/community/dazhouzhoubianb/', 4),
                               ('https://bazhong.anjuke.com/community/pingchangxian/', 199),
                               ('https://bazhong.anjuke.com/community/bazhongzhoubian/', 5),
                               ('https://suining.anjuke.com/community/chuanshanb/', 730),
                               ('https://suining.anjuke.com/community/anju/', 34),
                               ('https://suining.anjuke.com/community/pengxia/', 4),
                               ('https://suining.anjuke.com/community/shehong/', 389),
                               ('https://suining.anjuke.com/community/dayingb/', 121),
                               ('https://suining.anjuke.com/community/suiningzhoubian/', 13),
                               ('https://meishan.anjuke.com/community/renshouxian/', 124),
                               ('https://meishan.anjuke.com/community/danlingxian/', 2),
                               ('https://meishan.anjuke.com/community/pengshanxian/', 98),
                               ('https://meishan.anjuke.com/community/qingshenxian/', 1),
                               ('https://meishan.anjuke.com/community/dongpoqu/', 404),
                               ('https://meishan.anjuke.com/community/hongyaxian/', 39),
                               ('https://deyang.anjuke.com/community/yang/', 802),
                               ('https://deyang.anjuke.com/community/guanghan/', 222),
                               ('https://deyang.anjuke.com/community/shi/',213),
                               ('https://deyang.anjuke.com/community/mianzhu/', 96),
                               ('https://deyang.anjuke.com/community/luojiang/',89),
                               ('https://deyang.anjuke.com/community/zhongjiang/', 148),
                               ('https://deyang.anjuke.com/community/deyangzhoubian/', 4),
                               ('https://guangan.anjuke.com/community/guanganbc/', 182),
                               ('https://guangan.anjuke.com/community/guanganchengnanb/', 167),
                               ('https://guangan.anjuke.com/community/guanganchengbeib/', 33),
                               ('https://guangan.anjuke.com/community/yuechi/', 130),
                               ('https://guangan.anjuke.com/community/hua/', 48),
                               ('https://guangan.anjuke.com/community/linshui/', 100),
                               ('https://guangan.anjuke.com/community/wusheng/', 62),
                               ('https://guangan.anjuke.com/community/qitabc/', 12),
                               ('https://yaan.anjuke.com/community/yuchengqu/', 34),
                               ('https://aba.anjuke.com/community/maerkangxian/', 2),
                               ('https://aba.anjuke.com/community/wenchuanxian/', 2),
                               ('https://aba.anjuke.com/community/xiaojinxian/', 2),
                               ('https://aba.anjuke.com/community/maoxian/', 2),
                               ('https://aba.anjuke.com/community/songpanxian/', 2),
                               ('https://aba.anjuke.com/community/jiuzhaigouxian/', 3),
                               ('https://aba.anjuke.com/community/lixianab/', 2),
                               ('https://aba.anjuke.com/community/jinchuan/', 2),
                               ('https://aba.anjuke.com/community/heshuiab/', 2),
                               ('https://aba.anjuke.com/community/rangtang/', 2),
                               ('https://aba.anjuke.com/community/abaab/', 2),
                               ('https://aba.anjuke.com/community/ruoergai/', 9),
                               ('https://aba.anjuke.com/community/hongyuanab/', 2),
                               ('https://ganzi.anjuke.com/community/ganzixian/', 2),
                               ('https://ganzi.anjuke.com/community/jiulongb/', 2),
                               ('https://ganzi.anjuke.com/community/yajiang/', 2),
                               ('https://ganzi.anjuke.com/community/daofu/', 2),
                               ('https://ganzi.anjuke.com/community/luhuo/', 2),
                               ('https://ganzi.anjuke.com/community/xinlongc/', 2),
                               ('https://ganzi.anjuke.com/community/baiyu/', 2),
                               ('https://ganzi.anjuke.com/community/shiquc/', 2),
                               ('https://ganzi.anjuke.com/community/seda/', 2),
                               ('https://ganzi.anjuke.com/community/litang/', 2),
                               ('https://ganzi.anjuke.com/community/batang/', 2),
                               ('https://ganzi.anjuke.com/community/xiangchengb/', 2),
                               ('https://ganzi.anjuke.com/community/daocheng/', 2),
                               ('https://ganzi.anjuke.com/community/derong/', 15),
                               ('https://ganzi.anjuke.com/community/kangdingxian/', 3),
                               ('https://ganzi.anjuke.com/community/danbaxian/', 2),
                               ('https://ganzi.anjuke.com/community/ludingxian/', 2),
                               ('https://ganzi.anjuke.com/community/degexian/', 2),
                               ('https://liangshan.anjuke.com/community/xichangshi/', 435),
                               ('https://liangshan.anjuke.com/community/huid/', 3),
                               ('https://liangshan.anjuke.com/community/dechang/', 4),
                               ('https://liangshan.anjuke.com/community/huili/', 9),
                               ('https://liangshan.anjuke.com/community/liangshanzhoubian/', 3),
                               ]
        self.url_list = []
        self.info_list = []

    def start_crawler(self):
        for start_url in self.start_url_list:
            max_page = int(start_url[1] / 30) + 1
            for page in range(1, max_page + 1):
                url = start_url[0] + 'p{}/'.format(str(page))
                if len(self.url_list) == 50:
                    self.run()
                    self.url_list.clear()
                    continue
                else:
                    self.url_list.append(url)
        if len(self.url_list)>0:
            self.run()

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
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error(e)
        #     return
        r = self.send_url(url)
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

    @retry(delay=2,logger=log)
    def send_url(self,url):
        res = requests.get(url=url, headers=self.headers, proxies=p)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res.text:
            raise VerifyError('出现滑块验证码')
        return res

class VerifyError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


if __name__ == '__main__':
    anjuke = AnJuKe()
    anjuke.start_crawler()
