import re
import asyncio
import aiohttp
import requests
from lxml import etree
from usa_estate import SoldPrice, ListedPrice, RentPrice
from lib.log import LogHandler

log = LogHandler(__name__)
source = 'trulia'


class Trulia:
    def __init__(self):
        self.start_url = 'http://www.trulia.com/sitemap/'
        self.proxy = {'http': 'http://127.0.0.1:8787'}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
            'X-DevTools-Emulate-Network-Conditions-Client-Id': '48E14F47DF0865F8A307E8684F17E6BC'
        }

    def start_crawler(self):
        self.state_map()

    def state_map(self):
        response = requests.get(self.start_url, proxies=self.proxy, headers=self.headers)
        html = etree.HTML(response.content.decode())
        state_list = html.xpath("//ul[@class='real-estate-markets']/li")
        for state in state_list:
            temp_url = state.xpath('./a/@href')[0]
            state_name = state.xpath('./a/@title')[0]
            self.county(temp_url, state_name)

    def county(self, temp_url, state_name):
        state_url = 'http://www.trulia.com' + temp_url
        county_res = requests.get(state_url, proxies=self.proxy, headers=self.headers)
        html = etree.HTML(county_res.content.decode())
        county_list = html.xpath("//ul[@class='all-counties-sitemap-links']/li")
        for county in county_list:
            temp_url = county.xpath('./a/@href')[0]
            county_name = county.xpath('./a/@title')[0]
            # self.sold_fetch()
            # self.rent_fetch()
            self.sale_fetch(temp_url, county_name, state_name)

    def sold_fetch(self):
        pass

    def rent_fetch(self):
        pass

    def sale_fetch(self, temp_url, county_name, state_name):
        url = 'http://www.trulia.com' + temp_url
        res = requests.get(url, proxies=self.proxy, headers=self.headers)
        html = etree.HTML(res.content.decode())
        temp_url = html.xpath("//div[@class='miniCol24 xxsCol12']/a/@href")[0]
        allinfo = 'http://www.trulia.com' + temp_url
        sale_res = requests.get(allinfo, proxies=self.proxy, headers=self.headers)
        page = 1
        loop = asyncio.get_event_loop()
        while True:
            page_url = allinfo + '{}_p/'.format(str(page))
            page_res = requests.get(page_url, proxies=self.proxy, headers=self.headers)
            if 'Your search does not match any homes.' in sale_res.content.decode():
                break
            page_html = etree.HTML(page_res.content.decode())
            house_list = page_html.xpath("//ul[@class='mvn row']/li//a[@class='tileLink']/@href")
            tasks = [self.sale_crawler(tmpurl, county_name, state_name) for tmpurl in house_list]
            loop.run_until_complete(asyncio.wait(tasks))
            page += 1

    async def sale_crawler(self, tmpurl, county_name, state_name):
        await self.sale_parse(await self.detail_request(tmpurl), county_name, state_name)

    async def detail_request(self, tmpurl):
        url = 'http://www.trulia.com' + tmpurl
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    con = await resp.text()
                    return con
                else:
                    log.error('{}请求失败'.format(url))
                    con = None
                    return con

    async def sale_parse(self, con, county_name, state_name):
        if con is None:
            return
        else:
            try:
                html = etree.HTML(con)
                baths = re.search('"bathrooms":"(.*?) baths","bedrooms":"(.*?) beds"', con).group(1)
                beds = re.search('"bathrooms":"(.*?) baths","bedrooms":"(.*?) beds"', con).group(2)
                type = html.xpath("/html/body/div[7]/div[1]/div/div[2]/div[1]/ul/li[1]/text()")[0]
                sale_price = re.search('current":(\d+),', con).group(1)
                streetnum = re.search('streetNumber":"(.*?)",', con).group(1)
                street = re.search('street":"(.*?)",', con).group(1)
                apartnumber = re.search('apartmentNumber":"(.*?)",', con).group(1)
                county = county_name
                state = state_name
                zipcode = re.search('"zip":"(.*?)",', con).group(1)
                size = re.search('"sqft":"(\d+)",', con).group(1)
                hoa = re.search('monthlyHOA":(.*?)\}', con).group(1)
                dealdate = re.search('LISTING INFORMATION.*?Updated: (.*?)</span', con, re.S | re.M).group(1)
                avgprice = re.search('\$(.*?)/sqft</li', con).group(1)
                if len(re.findall('Built in (\d+)', con)) > 0:
                    year_built = re.findall('Built in (\d+)', con)[0]
                else:
                    year_built = None
                floor = None
                total_floor = None

                s = SoldPrice(price=int(sale_price), avg_price=avgprice, deal_date=dealdate,
                              baths=baths, bed=beds, source=source, state=state, county=county,
                              zipcode=zipcode, street_number=streetnum, street=street,
                              apartment_number=apartnumber, house_type=type, size=size,
                              year_built=year_built, floor=floor, total_floor=total_floor, HOAfee=int(hoa))
                s.soldprice_insert()
            except Exception as e:
                log.error('解析入库失败,error={}'.format(e))
