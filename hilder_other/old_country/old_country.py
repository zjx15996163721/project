import requests
import re
import yaml
from lib.mongo import Mongo
import time

setting = yaml.load(open('config.yaml'))

connect = Mongo(setting['old_county']['mongo']['host']).connect
coll = connect[setting['old_county']['mongo']['db']][setting['old_county']['mongo']['collection']]


class Country:
    def __init__(self):
        self.url = 'https://cun.isoyu.com/laoxiangcun/PufXOt1NNtLrTj.html'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
            'upgrade-insecure-requests': '1',
            'referer': 'https://cun.isoyu.com/laoxiangcun/QkNPPtLnGOxURNRJPuDNGEDqRj1EPuSGW0SnVREoH0pfIQSoVGNiHt.html',
            'cookie': 'Hm_lvt_b564ae7a10584a875141e8357b5b20d1=1525313743,1525315892; Hm_lvt_b4b83be64d9a09729ed6dee742b57543=1525313743,1525315892; Hm_lpvt_b4b83be64d9a09729ed6dee742b57543=1525324259; Hm_lpvt_b564ae7a10584a875141e8357b5b20d1=1525324259',
        }

    def start(self):
        time.sleep(0.1)
        response = requests.get(self.url, headers=self.headers)
        html = response.text
        province_html = re.search('<ul data-role="listview">.*?</ul>', html, re.S | re.M).group()
        province_str_list = re.findall('<li>.*?</li>', province_html, re.S | re.M)
        for i in province_str_list:
            province_url = 'https://cun.isoyu.com/' + re.search('<a href="(.*?)"', i, re.S | re.M).group(1)
            province_name = re.search('<a href=.*?>(.*?)<', i, re.S | re.M).group(1)
            try:
                self.get_region(province_url, province_name)
            except Exception as e:
                print('省错误，url={}'.format(province_url), e)

    def get_region(self, province_url, province_name):
        time.sleep(1)
        response = requests.get(province_url, headers=self.headers)
        html = response.text
        region_html_list = re.findall('data-role="collapsible".*?/div>', html, re.S | re.M)
        for i in region_html_list:
            region_name = re.search('<h1>(.*?)</h1>', i, re.S | re.M).group(1)
            county_html_list = re.findall('<li>.*?</li>', i, re.S | re.M)
            for j in county_html_list:
                county_url = 'https://cun.isoyu.com/' + re.search('href="(.*?)"', j, re.S | re.M).group(1)
                county_name = re.search('<a.*?>(.*?)</a>', j, re.S | re.M).group(1)
                try:
                    self.get_county(county_url, province_name, region_name, county_name)
                except Exception as e:
                    print('县错误，url={}'.format(county_url), e)

    def get_county(self, county_url, province_name, region_name, county_name):
        time.sleep(1)
        response = requests.get(county_url, headers=self.headers)
        html = response.text
        village_html_list = re.findall('data-role="collapsible".*?</div>', html, re.S | re.M)
        for i in village_html_list:
            village_name = re.search('<h1>(.*?)</h1>', i, re.S | re.M).group(1)
            burg_html_list = re.findall('<li>.*?</li>', i, re.S | re.M)
            for j in burg_html_list:
                burg_name = re.search('<a.*?>(.*?)</a>', j, re.S | re.M).group(1)
                data = {
                    'province_name': province_name,
                    'region_name': region_name,
                    'county_name': county_name,
                    'village_name': village_name,
                    'burg_name': burg_name,
                }
                print(data)
                coll.insert_one(data)


if __name__ == '__main__':
    c = Country()
    c.start()
