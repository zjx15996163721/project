import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
import threading
from lib.log import LogHandler
from retry import retry
log = LogHandler('lianjia')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['hilder_gv']['sichuan']
sichuan_city_list = ['成都', '绵阳', '宜宾', '自贡', '攀枝花',
                 '广元', '乐山', '南充', '泸州', '资阳',
                 '内江', '达州', '巴中', '遂宁', '眉山',
                 '德阳', '广安', '雅安', '阿坝州','甘孜州','凉山州']



class Lianjia:

    def __init__(self):
        self.headers = {
            'Cookie': 'lianjia_uuid=44a258db-4e00-4541-997c-57f4f3c117c1; _smt_uid=5c077f11.54f9c61d; gr_user_id=34c329d5-abde-48c8-8e92-164aeb1967c4; UM_distinctid=1677d485e781e8-08ba54e7ba4e7e-35607402-1fa400-1677d485e7994; _jzqc=1; _ga=GA1.2.130576672.1543995159; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1543995154,1544173828,1544173833; _jzqy=1.1544173829.1544173833.2.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6%E5%9C%B0%E4%BA%A7.jzqsr=baidu; _jzqx=1.1544430132.1544608309.5.jzqsr=bj%2Elianjia%2Ecom|jzqct=/.jzqsr=bj%2Elianjia%2Ecom|jzqct=/chengjiao/fengtai/; _gid=GA1.2.2020321299.1545103818; lianjia_ssid=b653ca99-45ef-4791-adbc-8cc15e705d04; _jzqa=1.4552267029258056000.1543995157.1545189315.1545206059.32; _jzqckmp=1; Qs_lvt_200116=1544798856%2C1545206539; Qs_pv_200116=235986746040596130%2C4405708339866472400%2C1972589321055627500%2C3526812790752574500%2C3163296021085384000; gr_session_id_a1a50f141657a94e=1aed3e59-04fb-4f93-90bc-5637149eeea8; gr_session_id_a1a50f141657a94e_1aed3e59-04fb-4f93-90bc-5637149eeea8=true; select_city=310000; all-lj=dafad6dd721afb903f2a315ab2f72633; TY_SESSION_ID=3a1d7567-ccca-4314-a3df-f1551037dceb; CNZZDATA1253492439=1920645834-1545204530-https%253A%252F%252Fbj.lianjia.com%252F%7C1545204530; CNZZDATA1254525948=828434328-1545203924-https%253A%252F%252Fbj.lianjia.com%252F%7C1545203924; CNZZDATA1255633284=1412891771-1545206158-https%253A%252F%252Fbj.lianjia.com%252F%7C1545206158; CNZZDATA1255604082=774544540-1545204688-https%253A%252F%252Fbj.lianjia.com%252F%7C1545204688; _qzjc=1; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1545207895; _qzja=1.386660674.1545207885583.1545207885583.1545207885583.1545207891886.1545207895471.0.0.0.5.1; _qzjb=1.1545207885583.5.0.0.0; _qzjto=5.1.0; _jzqb=1.134.10.1545206059.1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.start_url = [('https://cd.lianjia.com/xiaoqu/',"成都")]


    def start_crawler(self):
        for i in self.start_url:
            threading.Thread(target=self.start_request, args=(i, )).start()

    def start_request(self, info):
        city_name = info[1]
        url = info[0]
        r = self.send_url(url)
        tree = etree.HTML(r.text)
        city_list = tree.xpath("/html/body/div[3]/div[1]/dl[2]/dd/div/div/a")
        for city in city_list:
            city_link = city.xpath('./@href')[0]
            city_url = url + re.search('/xiaoqu/(.*?)/', city_link, re.S | re.M).group(1) + '/'
            region = city.xpath('./text()')[0]
            self.get_page_url(city_url, region, city_name)

    def get_page_url(self, url, region, city):
        maxpage = self.get_page(url)
        if maxpage:
            for page in range(1, int(maxpage)+1):
                link = url + 'pg{}/'.format(str(page))
                self.get_all_district_url(link, region, city)

    def get_page(self, url):
        r = self.send_url(url)
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error('请求失败 source={}, url={}, e={}'.format('链家在线', url, e))
        #     return
        try:
            num = re.search('共找到<span> (.*?) </span>个小区', r.text, re.S | re.M).group(1)
            max_page = int(int(num)/30) + 1
            return max_page
        except Exception as e:
            log.error(e)
            return

    def get_all_district_url(self, url, region, city):
        r = self.send_url(url)
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error('请求失败　url={}, e={}'.format(url, e))
        #     return
        tree = etree.HTML(r.text)
        detail_list = tree.xpath('/html/body/div[4]/div[1]/ul/li')
        for detail_link in detail_list:
            link = detail_link.xpath("./div[1]/div[1]/a/@href")[0]
            district_name = detail_link.xpath("./div[1]/div[1]/a/text()")[0]
            self.parse(link, district_name, region, city)

    def parse(self, url, district_name, region, city):
        r = self.send_url(url)
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error('请求失败　url={}, e={}'.format(url, e))
        #     return
        try:
            household_count = re.search('房屋总数</span><.*?>(\d+)户<', r.text, re.S| re.M).group(1)
        except:
            household_count = None
        try:
            estate_charge = re.search('物业费用</span><.*?>(.*?)元', r.text, re.S | re.M).group(1)
        except:
            estate_charge = None
        try:
            complete_time = re.search('建筑年代</span><.*?>(\d+)年', r.text, re.S | re.M).group(1)
        except:
            complete_time = None
        try:
            address = re.search('<div class="detailDesc">(.*?)</div>', r.text, re.S | re.M).group(1)
        except:
            address = None
        data = {
            'source': 'lianjia',
            'city': city,
            'region': region,
            'district_name': district_name,
            'complete_time': complete_time,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address,
            'url': url
        }
        if not collection.find_one(data):
            try:
                collection.insert_one(data)
                log.info('插入一条数据{}'.format(data))
            except Exception as e:
                log.error('数据唯一索引冲突')
        else:
            log.info('重复数据')

    @retry(delay=2,logger=log)
    def send_url(self,url):
        res = requests.get(url=url, headers=self.headers, proxies=p)
        return res



if __name__ == '__main__':
    lianjia = Lianjia()
    lianjia.start_crawler()

