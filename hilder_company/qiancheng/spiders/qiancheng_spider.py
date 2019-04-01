import scrapy
from scrapy import Request
from lxml import etree
import re
import datetime
from qiancheng.items import QianchengItem


class QianCheng(scrapy.Spider):
    name = 'qiancheng'
    headers = {
        'Host': 'jobs.51job.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    
    def start_requests(self):
        for i in range(0, 9999999):
            url = 'https://jobs.51job.com/all/co' + str(i) + '.html'
            yield Request(url=url, headers=self.headers, callback=self.get_info, meta={'url': url})

    def get_info(self, response):
        company_url = response.meta['url']
        company_id = re.search('https://jobs\.51job\.com/all/co(\d+)\.html', company_url).group(1)
        company_source = '51job'
        tree = etree.HTML(response.text)
        item = QianchengItem()
        item['company_source'] = company_source
        item['company_id'] = company_id
        item['url'] = company_url
        try:
            company_name = tree.xpath("//div[@class='tHeader tHCop']/div[1]/h1/text()")[0]
            item['company_name'] = company_name
        except Exception as e:
            print('名称解析错误 url={}'.format(company_url))
            item['company_name'] = None
        try:
            address1 = tree.xpath("/html/body/div[2]/div[2]/div[3]/div[2]/div/p/text()")[1]
            address2 = address1
            if '(' in address2:
                address = address2.split('(')[0].replace("\r", "").replace("\n", "").replace(" ", "")
            else:
                address = address2.replace("\r", "").replace("\n", "").replace(" ", "")
            item['address'] = address
        except Exception as e:
            print('地址解析错误 url={}'.format(company_url))
            item['address'] = None
        try:
            company_info = tree.xpath("//div[@class='con_txt']")[0]
            company_info = company_info.xpath('string(.)')
            item['company_info'] = company_info
        except Exception as e:
            print('公司信息解析错误 url={}'.format(company_url))
            item['company_info'] = None
        try:
            company_size_business_info = tree.xpath("//p[@class='ltype']")[0]
            company_size_business_info_str = company_size_business_info.xpath('string(.)')

            company_size_business = company_size_business_info_str.split('|')
            if len(company_size_business) == 3:
                company_size = company_size_business[1]
                business = company_size_business[2]
                item['company_size'] = company_size
                item['business'] = business
            else:
                try:
                    num = re.search("(\d+)", company_size_business_info_str, re.S | re.M).group(1)
                    if num in company_size_business[0]:
                        company_size = company_size_business[0]
                        business = company_size_business[1]
                        item['company_size'] = company_size
                        item['business'] = business
                    else:
                        company_size = company_size_business[1]
                        business = None
                        item['company_size'] = company_size
                        item['business'] = business
                except:
                    company_size = None
                    business = company_size_business[1]
                    item['company_size'] = company_size
                    item['business'] = business
        except Exception as e:
            print('公司规模，行业解析错误 url={}'.format(company_url))
            item['company_size'] = None
            item['business'] = None
        item['city'] = None
        item['region'] = None
        item['company_short_info'] = None
        item['development_stage'] = None
        item['registration_time'] = None
        item['registered_capital'] = None
        item['operating_period'] = None
        item['crawler_time'] = datetime.datetime.now()
        yield item
