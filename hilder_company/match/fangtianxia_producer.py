"""
房天下网站抓取
http://www.fang.com/SoufunFamily.htm
"""
import requests
from lxml import etree
import re
import pika
import json
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
p = p.get_one(proxies_number=2)

log = LogHandler('房天下')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='fangtianxia')


class FangTianXia:

    def __init__(self, proxies):
        self.headers = {
            'Host': 'newhouse.fang.com',
            'Cookie': 'Integrateactivity=notincludemc; global_cookie=5j8ubb0m4ednyooi5plr4yd8023joff8i9y; __utmc=147393320; showAdhz=1; __utmz=147393320.1542792924.4.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E6%88%BF%E5%A4%A9%E4%B8%8B; SoufunSessionID_Office=3_1542792936_3838; searchLabelN=3_1542793018_497%5B%3A%7C%40%7C%3A%5D87edc19feb1e313acb8638b127cf7805; searchConN=3_1542793018_1305%5B%3A%7C%40%7C%3A%5D91b9570c97f179b6d0a5865bfdd42d21; __jsluid=c6f2cc7609b88bf2416db51ba04adf7d; newhouse_user_guid=230569EE-C2C7-F49E-C18B-B0D9CAB41DEC; newhouse_chat_guid=ADC9BD35-2591-E113-7387-3BDB937D9173; sf_source=; s=; showAdbj=1; showAdsh=1; new_search_uid=30addff46ca262cdb78c2a04acfe9736; showAdquanguo=1; showAdzhuzhou=1; showAdmacau=1; showAdanyang=1; vh_newhouse=3_1542799696_1496%5B%3A%7C%40%7C%3A%5Dc7211a5c086643560ed38e963352a1de; Captcha=3476637A6571767838613276454776334E626E46784F7950444B714F34576348743235626F38685A37534F4E466A4543494D795377493878374E4B69696B7A4B4974514A625861346149303D; __utma=147393320.1199726105.1542094480.1542792924.1542808263.5; xfAdvLunbo=; __utmt_t3=1; __utmt_t4=1; indexAdvLunbo=lb_ad3%2C0%7Clb_ad6%2C0; city=bj; unique_cookie=U_5j8ubb0m4ednyooi5plr4yd8023joff8i9y*133; __utmt_t0=1; __utmt_t1=1; __utmt_t2=1; __utmb=147393320.47.10.1542808263',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.proxies = proxies
        self.start_url = 'http://www.fang.com/SoufunFamily.htm'

    def start_crawler(self):
        r = requests.get(url=self.start_url, headers=self.headers, proxies=self.proxies)
        tree = etree.HTML(r.text)
        city_list = tree.xpath("//div[@class='onCont']/table/tr/td[2]/a")
        city_dict = {}
        for city in city_list:
            city_name = city.xpath("./text()")[0]
            city_url = city.xpath("./@href")[0]
            city_dict[city_name] = city_url
        self.get_office_list(city_dict)

    def get_office_list(self, city_dict):
        for city in city_dict:
            print(city)
            print(city_dict[city])

            if '北京' in city:
                city_link = 'http://newhouse.fang.com/house/s/a75-b91/?ctm=1.bj.xf_search.page.2'
            else:
                try:
                    city_link = re.search('(.*)fang\.com', city_dict[city]).group(1) + 'newhouse.fang.com/house/s/a75-b91'
                except:
                    continue

            max_page = self.get_max_page(city_link)
            print(max_page)
            if max_page is None:
                self.get_all_links(city_link, city)
            else:
                for page in range(1, int(max_page)+1):
                    link = re.search('(.*)fang\.com', city_dict[city]).group(1) + 'newhouse.fang.com/house/s/a75-b9{}'.format(str(page))
                    print(link)
                    self.get_all_links(link, city)

    def get_max_page(self, url):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 url={} e={}'.format(url, e))
            return
        if '抱歉，没有找到' in r.text:
            return
        try:
            tree = etree.HTML(r.text)
            max_page_info = tree.xpath("//div[@class='page']/ul/li[2]/a/@href")[-1]
            max_page = re.search('/house/s/a75-b9(\d+)/', max_page_info).group(1)
            return max_page
        except:
            return

    def get_all_links(self, url, city):
        try:
            r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('请求失败 url={} e={}'.format(url, e))
            return
        try:
            tree = etree.HTML(r.content.decode('gbk'))
            info_list = tree.xpath('//div[@id="newhouse_loupai_list"]/ul/li')
        except Exception as e:
            log.error('解析错误 url={} e={}'.format(url, e))
            return
        for info in info_list:
            try:
                link = info.xpath("./div/div[2]/div[1]/div[1]/a/@href")[0]
                id_link = info.xpath("./div/div[2]/div[@class='notice']/div[2]/@onclick")[0]
            except Exception as e:
                log.error('取不到链接和ID url={} e={}'.format(url, e))
                continue
            building_id = re.search("shoucangProcess\('(\d+)',", id_link, re.S | re.M).group(1)
            if 'http' in link:
                half_url = re.search('(.*)com', link, re.S | re.M).group(1)
                detail_url = half_url + 'com/house/' + str(building_id) + '/housedetail.htm'
                data = {
                    'city': city,
                    'link': detail_url
                }
                channel.basic_publish(exchange='',
                                      routing_key='fangtianxia',
                                      body=json.dumps(data))
                log.info('一条数据放队列 url={}'.format(data))
            else:
                detail_url = 'http:' + link + 'house/' + str(building_id) + '/housedetail.htm'
                data = {
                    'city': city,
                    'link': detail_url
                }
                channel.basic_publish(exchange='',
                                      routing_key='fangtianxia',
                                      body=json.dumps(data))
                log.info('一条数据放队列 url={}'.format(data))


if __name__ == '__main__':
    fang = FangTianXia(p)
    fang.start_crawler()