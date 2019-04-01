import aiohttp
import asyncio
import re
import requests
from company_info import Company
from lxml import etree
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
from source_config import Category, City, get_sqlalchemy_session

log = LogHandler(__name__)
db_session = get_sqlalchemy_session()
p = Proxies()


class Liepin:
    def __init__(self, proxies):
        self.source = 'liepin'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.proxies = proxies

    def start_crawler(self):
        city_list = db_session.query(City).filter_by(source='liepin')
        cate_list = db_session.query(Category).filter_by(source='liepin')
        print(cate_list)
        print(city_list)
        for city in city_list:
            city_id = city.request_parameter
            city_name = city.name
            print(city_name)
            for cate in cate_list:
                cate_id = cate.request_parameter
                index_url = 'https://www.liepin.com/company/' + city_id + '-' + cate_id
                self.fetch_index(index_url)

    def fetch_index(self, url):
        res = requests.get(url, headers=self.headers, proxies=next(p))
        self.index_parse(url, res)

    def index_parse(self, url, resp):
        page = re.search('共(\d+)页', resp.content.decode())
        if page is None:
            log.info('没有分页')
            self.fetch_page(url, 1)
        else:
            print(page)
            pagecount = page.group(1)
            self.fetch_page(url, pagecount)

    def fetch_page(self, url, page):
        for i in range(int(page)):
            if i == 0:
                page_res = requests.get(url, headers=self.headers, proxies=next(p))
            else:
                page_url = url + '/pn' + str(i)
                page_res = requests.get(page_url, headers=self.headers, proxies=next(p))
            self.page_parse(page_res)

    def page_parse(self, page_res):
        html = etree.HTML(page_res.content.decode())
        company_list = html.xpath("//p[@class='company-name']/a/@href")
        loop = asyncio.get_event_loop()
        tasks = [self.company_detail(url) for url in company_list]
        loop.run_until_complete(asyncio.wait(tasks))

    async def company_detail(self, url):
        await self.detail_parse(await self.detail_request(url))

    async def detail_request(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, proxy=self.proxies) as resp:
                    if resp.status == 200:
                        con = await resp.text()
                        return con
                    else:
                        log.error('{}请求失败'.format(url))
            except:
                log.error('{}请求失败'.format(url))

    async def detail_parse(self, res):
        html = etree.HTML(res)
        try:
            company_id = re.search('ecomp_id : "(\d+)"', res).group(1)
            company = Company(company_id, self.source)
            company.company_name = html.xpath('//h1/text()')[0]
            company.address = re.search('公司地址：</span>(.*?)</li>', res).group(1)
            company.city = re.search('data-city="(.*?)"', res).group(1)
            if html.xpath("//p[@class='profile']/text()") is not None:
                company.company_info = html.xpath("//p[@class='profile']/text()")[0].strip()
            if re.search('公司规模：</span>(.*?)</li>', res) is not None:
                company.company_size = re.search('公司规模：</span>(.*?)</li>', res).group(1)
            if re.search('经营期限：(.*?)</li', res) is not None:
                company.operating_period = re.search('经营期限：(.*?)</li', res).group(1)
            if re.search('注册时间：(.*?)</li', res) is not None:
                company.registration_time = re.search('注册时间：(.*?)</li', res).group(1)
            if re.search('注册资本：(.*?)</li', res) is not None:
                company.registered_capital = re.search('注册资本：(.*?)</li', res).group(1)
            if html.xpath("//a[@class='comp-industry']/text()") is not None:
                company.business = html.xpath("//a[@class='comp-industry']/text()")[0]
            company.insert_db()
        except Exception as e:
            log.error('解析失败{}'.format(e))
