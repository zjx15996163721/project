import requests
from lib.proxy_iterator import Proxies
from lxml import etree
from lib.log import LogHandler
from pymongo import MongoClient
import datetime
log = LogHandler('拉钩')
p = Proxies()
p = p.get_one(proxies_number=1)
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
BI_collection = m['lagou_BI']['lagou_BI']
BI_collection_backups = m['lagou_BI']['lagou_BI_backups']


class LagouBI:
    def __init__(self):
        self.headers = {
            'Referer': 'https://www.lagou.com/jobs/list_bi?px=default&city=%E4%B8%8A%E6%B5%B7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie': 'JSESSIONID=ABAAABAAADEAAFICD550FF7082FE58BD51F04E2EB088D5D; user_trace_token=20181011183208-d76e33bd-cc63-47d0-8da7-f32377c0e022; _ga=GA1.2.1724894585.1539253931; _gid=GA1.2.37780505.1539253931; LGUID=20181011183209-e825388e-cd40-11e8-bbb2-5254005c3644; WEBTJ-ID=20181012110759-166663ebaff631-00b9d0fafced7e-8383268-2073600-166663ebb00ab; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539253931,1539313679,1539313688; index_location_city=%E4%B8%8A%E6%B5%B7; TG-TRACK-CODE=search_code; SEARCH_ID=2639969b5eb6411eb06d8505365c7440; LGSID=20181013143935-bfd94b56-ceb2-11e8-b23e-525400f775ce; X_HTTP_TOKEN=245553eecf535bb8aa958e4209ec6169; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221666c8685478e9-0085747f11ad55-8383268-2073600-1666c86854827e%22%2C%22%24device_id%22%3A%221666c8685478e9-0085747f11ad55-8383268-2073600-1666c86854827e%22%7D; sajssdk_2015_cross_new_user=1; LGRID=20181013162519-853bc6be-cec1-11e8-bbe1-5254005c3644; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539419123'
        }
        self.url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false'

    def get_url_list(self):
        for page in range(1, 10):
            data = {
                'first': False,
                'pn': page,
                'kd': 'bi'
            }
            r = requests.post(url=self.url, data=data, headers=self.headers, proxies=p)
            info_list = r.json()['content']['positionResult']['result']
            for info in info_list:
                # 城市
                city = info['city']
                # 公司全名
                companyFullName = info['companyFullName']
                # 公司ID
                companyId = info['companyId']
                # 公司短称
                companyShortName = info['companyShortName']
                # 公司规模
                companySize = info['companySize']
                # 区域
                region = info['district']
                # 学历要求
                education = info['education']
                # 行业
                business = info['industryField']
                # 详情ID todo
                positionId = info['positionId']
                # 职位
                positionName = info['positionName']
                # 薪资
                salary = info['salary']
                # 工作经验
                workYear = info['workYear']
                self.get_detail(positionId, city, companyFullName, companyId, companyShortName, companySize, region, education, business, positionName, salary, workYear)

    def get_detail(self, positionId, city, companyFullName, companyId, companyShortName, companySize, region, education, business, positionName, salary, workYear):
        url = 'https://www.lagou.com/jobs/{}.html'.format(str(positionId))
        r = requests.get(url=url, headers=self.headers, proxies=p)
        tree = etree.HTML(r.text)
        try:
            requirements_info_list = tree.xpath("//div[@class='content_l fl']/dl[1]/dd[2]/div//p")
            requirements_list = []
            for i in requirements_info_list:
                requirements = i.xpath('string(.)')
                requirements_list.append(requirements)
            data = {
                'city': city,
                'region': region,
                'companyFullName': companyFullName,
                'companyId': companyId,
                'companyShortName': companyShortName,
                'companySize': companySize,
                'education': education,
                'business': business,
                'positionName': positionName,
                'salary': salary,
                'workYear': workYear,
                'requirements': requirements_list,
                'positionId': positionId,
                'url': url,
                'crawler_time': datetime.datetime.now()
            }
            BI_collection.insert_one(data)
            log.info('插入一条数据 data={}'.format(data))
        except:
            log.error('解析错误 url={}'.format(url))


if __name__ == '__main__':
    lagou = LagouBI()
    lagou.get_url_list()