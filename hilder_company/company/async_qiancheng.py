import requests
import aiohttp
import asyncio
from lib.proxy_iterator import Proxies
from lxml import etree
import re
# from company_info import Company
# from company_info import check_company
# p = Proxies()


class Jobs(object):
    def __init__(self):
        self.headers = {
            'Host': 'jobs.51job.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }

    def get_all_links(self, num):
        url_list = []
        for i in range(1 + num, 1000 + num):
            url = 'https://jobs.51job.com/all/co' + str(i) + '.html'
            url_list.append(url)
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.run(url) for url in url_list]
            loop.run_until_complete(asyncio.wait(tasks))
        except Exception as e:
            print(e)

    async def run(self, url):
        try:
            # semaphore = asyncio.Semaphore(100)
            await self.get_info(await self.url_request(url), company_url=url)
        except Exception as e:
            print(e)

    async def url_request(self, url):
        print(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=self.headers) as response:
                if response.status == 200:
                    con = await response.text(encoding='gbk')
                    return con
                else:
                    print('请求失败')

    async def get_info(self, response, company_url):
        tree = etree.HTML(response)
        company_id = re.search('https://jobs\.51job\.com/all/co(\d+)\.html', company_url).group(1)
        company_source = '51job'
        print(company_id)
        # if check_company(company_source, company_id) is None:
        #     company = Company(company_id=company_id, company_source=company_source)
        #     company.company_id = company_id
        #     company.company_source = company_source
        #     company.url = company_url
        #     try:
        #         company_name = tree.xpath("//div[@class='tHeader tHCop']/div[1]/h1/text()")[0]
        #         company.company_name = company_name
        #     except Exception as e:
        #         print('名称解析错误 url={}'.format(company_url))
        #         company.company_name = None
        #     try:
        #         address1 = tree.xpath("/html/body/div[2]/div[2]/div[3]/div[2]/div/p/text()")[1]
        #         address2 = address1
        #         if '(' in address2:
        #             address = address2.split('(')[0].replace("\r", "").replace("\n", "").replace(" ", "")
        #         else:
        #             address = address2.replace("\r", "").replace("\n", "").replace(" ", "")
        #         company.address = address
        #     except Exception as e:
        #         print('地址解析错误 url={}'.format(company_url))
        #         company.address = None
        #     try:
        #         company_info = tree.xpath("//div[@class='con_txt']")[0]
        #         company_info = company_info.xpath('string(.)')
        #         company.company_info = company_info
        #     except Exception as e:
        #         print('公司信息解析错误 url={}'.format(company_url))
        #         company.company_info = None
        #     try:
        #         company_size_business_info = tree.xpath("//p[@class='ltype']")[0]
        #         company_size_business_info_str = company_size_business_info.xpath('string(.)')
        #
        #         company_size_business = company_size_business_info_str.split('|')
        #         if len(company_size_business) == 3:
        #             company_size = company_size_business[1]
        #             business = company_size_business[2]
        #             company.company_size = company_size
        #             company.business = business
        #         else:
        #             try:
        #                 num = re.search("(\d+)", company_size_business_info_str, re.S | re.M).group(1)
        #                 if num in company_size_business[0]:
        #                     company_size = company_size_business[0]
        #                     business = company_size_business[1]
        #                     company.company_size = company_size
        #                     company.business = business
        #                 else:
        #                     company_size = company_size_business[1]
        #                     business = None
        #                     company.company_size = company_size
        #                     company.business = business
        #             except:
        #                 company_size = None
        #                 business = company_size_business[1]
        #                 company.company_size = company_size
        #                 company.business = business
        #     except Exception as e:
        #         print('公司规模，行业解析错误 url={}'.format(company_url))
        #     company.insert_db()
        # else:
        #     print('库中已经存在')