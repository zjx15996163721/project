"""
从安居客781个城市中获取可以
"""

import requests
from lxml import etree
from retry import retry
from lib.log import LogHandler
from lib.standardization import  standard_city
from lib.proxy_iterator import Proxies
log = LogHandler('test_anjuke_producer_city')
p = Proxies()

class VerifyError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

@retry(logger=log,delay=2)
def send_url(proxies):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    url = 'https://www.anjuke.com/sy-city.html'
    requests.get('http://ip.dobel.cn/switch-ip', proxies=proxies)
    res = requests.get(url,headers=headers,proxies=proxies)
    html_res = etree.HTML(res.text)
    a_list = html_res.xpath('//div[@class="letter_city"]/ul/li/div[@class="city_list"]/a')
    print(len(a_list))
    if len(a_list) >0:
        return a_list
    else:
        raise VerifyError('城市列表为空，可能出现滑块验证码')

def analyse_city(proxies):
    a_list = send_url(proxies=proxies)
    real_city_list = []
    no_city_list = []
    for a in a_list:
        city_dict = {}
        city_url = a.xpath('@href')[0]
        city_name = a.xpath('text()')[0]
        result,real_city = standard_city(city_name)
        if result:
            city_dict[city_name] = city_url
            real_city_list.append(city_dict)
        else:
            city_dict[city_name] = city_url
            no_city_list.append(city_dict)

    print(len(real_city_list))
    print(real_city_list)
    print(len(no_city_list))
    print(no_city_list)




if __name__ == '__main__':
    analyse_city(next(p))
