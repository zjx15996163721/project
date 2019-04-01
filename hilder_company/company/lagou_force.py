import requests
from company_info import Company
from lxml import etree
from lib.log import LogHandler
import json
import pika
import re
import yaml

log = LogHandler('lagou_10_12')
settings = yaml.load(open('config.yaml'))
connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings['rabbitmq']['host'],
                                                               port=settings['rabbitmq']['port']))
channel = connection.channel()

class LagouProducer:
    def __init__(self):
        self.url = 'https://www.lagou.com/gongsi/'

    def start_produce(self, rabbit):
        for i in range(450000,470000):
            url = self.url + str(i) + '.html'
            print(url)
            rabbit.basic_publish(exchange='',
                                 routing_key='lagou_url',
                                 body=json.dumps(url),
                                 )

    def put_url_into_queue(self):
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673))
        rabbit = connection.channel()
        rabbit.queue_declare(queue='lagou_url')
        self.start_produce(rabbit)
        connection.close()


class LagouConsumer:
    def __init__(self, proxies):
        self.source = '拉钩'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Cookie': 'JSESSIONID=ABAAABAAAFCAAEGF4C9B5389EE98C2E7DD54C8B8A1414A2; _ga=GA1.2.1366137308.1528449246; user_trace_token=20180608171516-75154e69-6afc-11e8-971a-525400f775ce; LGUID=20180608171516-7515518f-6afc-11e8-971a-525400f775ce; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1529485519,1531191370; _gid=GA1.2.54377118.1531191370; index_location_city=%E5%8C%97%E4%BA%AC; LGSID=20180711150540-d1b43320-84d8-11e8-9a69-5254005c3644; TG-TRACK-CODE=index_navigation; SEARCH_ID=f9a229196ecf4bb9af91c7d37da83415; X_MIDDLE_TOKEN=0f7d2e0e5bed168eb564c8f8e97a9ded; X_HTTP_TOKEN=969ab535c830dee41a704cd5e7b48e80; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1531296958; LGRID=20180711161559-a4a4402d-84e2-11e8-9a69-5254005c3644'
        }
        self.proxies = proxies

    def start_consumer(self):
        # channel = connection.channel()
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(self.callback,
                              queue='lagou_url',
                              )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.send_message(json.loads(body.decode()))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_message(self, _url):
        try:
            result = requests.get(_url, proxies=self.proxies, headers=self.headers, timeout=5)
            # print(result.text)
        except Exception as e:
            log.error('请求错误,url={}'.format(_url))
            return
        if 'login' in result.url:
            print('登陆')
            # print(result.url)
        elif '本网站的Coder和PM私奔啦~~~具体范围团结湖附近，想八卦请看' in result.text:
            print('私奔啦')
        elif '这个公司的主页还在建设中…' in result.text:
            print('建设中')
        else:
            # 标准url:https://www.lagou.com/gongsi/441401.html
            company_id = re.search('gongsi/(.*?).html', _url).group(1)
            print(company_id)
            self.analyze_detail(result.text, company_id, _url)

    def analyze_detail(self, html, company_id, url):
        xpath_html = etree.HTML(html)
        company = Company(company_id=company_id, company_source=self.source)
        #转换为一段json字符串，几乎包含所有的信息
        # company_text = xpath_html.xpath("//script[@id='companyInfoData']/text()")
        # if company_text[0]:
        #     company_text = company_text[0]

        try:
            company_text = xpath_html.xpath("//script[@id='companyInfoData']/text()")[0]
        except:
            return
        company_info = json.loads(company_text)
        # 公司基本信息，包括人数，类型等
        baseinfo = company_info['baseInfo']
        # #地址列表，，里面包含很多地址信息
        # address = company_info['addressList'][0]
        # #里面包含公司基本信息，包括名字、简介等，
        # coreInfo = company_info['coreInfo']
        try:
            address = company_info['addressList'][0]
            company.address = address['detailAddress']#详细地址
            company.city = address['city']#城市
            company.company_name = company_info['coreInfo']['companyName']#公司名称
        except Exception as e:
            log.error('{}缺少必要字段,error={}'.format(url, e))
            return
        #长简介
        if company_info['introduction'].get('companyProfile'):
            company.company_info = company_info['introduction']['companyProfile']
        #短简介
        if company_info['coreInfo'].get('companyIntroduce'):
        # if company_info['coreInfo']['companyIntroduce']:
            company.company_short_info = company_info['coreInfo']['companyIntroduce']
        if baseinfo.get('industryField'):
            company.business = company_info['baseInfo']['industryField']
        if baseinfo.get('financeStage'):
            company.development_stage = company_info['baseInfo']['financeStage']
        if baseinfo.get('companySize'):
            company.company_size = company_info['baseInfo']['companySize']
        #所在区域
        if address.get('district'):
            company.region = address['district']
        company.url = url
        # result = company.serialization_info()
        # # print(result)
        company.insert_db()
