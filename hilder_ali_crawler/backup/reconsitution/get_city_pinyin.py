from reconsitution.city_num import add_city_dict
import requests
from lxml import etree
from lib.mongo import Mongo
from dianping.request_detail import request_get

headers = {
    'Cookie': "showNav=#nav-tab|0|1; navCtgScroll=200; showNav=javascript:; navCtgScroll=100; _lxsdk_cuid=16420be4e6bc8-01d123b766c0b2-39614101-1aeaa0-16420be4e6dc8; _lxsdk=16420be4e6bc8-01d123b766c0b2-39614101-1aeaa0-16420be4e6dc8; _hc.v=b83d3f69-dd86-b525-f3e0-70de4b48876e.1529557700; s_ViewType=10; aburl=1; wedchatguest=g-63166371096986944; __mta=223777060.1529993859415.1529996989084.1529996989087.4; Hm_lvt_e6f449471d3527d58c46e24efb4c343e=1530000088; Hm_lpvt_e6f449471d3527d58c46e24efb4c343e=1530000088; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; wed_user_path=55|0; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1529995150,1530062234; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1530062234; cityInfo=%7B%22cityId%22%3A952%2C%22cityEnName%22%3A%22huaining%22%2C%22cityName%22%3A%22%E6%80%80%E5%AE%81%E5%8E%BF%22%7D; cy=1; cye=shanghai; _lxsdk_s=1643ed097cd-de5-109-cf7%7C%7C142",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
}

ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-pro.abuyun.com", "port": "9010",
                                                     "user": "HRH476Q4A852N90P", "pass": "05BED1D0AF7F0715"}
proxy = {
    'http': ip,
    'https': ip
}

m = Mongo('114.80.150.196', 27777)
coll = m.connect['dianping']['city_region_hot']
for i in add_city_dict:
    pinyin = add_city_dict[i]
    city = i
    print(city)
    coll.remove({'city': i})
    url = 'http://www.dianping.com/' + pinyin + '/ch10'
    response = requests.get(url, headers=headers)
    html = response.text
    tree = etree.HTML(html)
    # # 收集菜系字典
    # cookie_list = tree.xpath('//*[@id="classfy"]/a')
    # kind_dict = {}
    # for kind in cookie_list:
    #     kind_url = kind.xpath('@href')[0]
    #     kind_code = kind_url.split('/')[-1]
    #     kind_name = kind.xpath('span/text()')[0]
    #     kind_dict[kind_code] = kind_name
    # # 收集热门商圈
    # hot_list = tree.xpath('//div[@id="bussi-nav"]/a')
    # hot_dict = {}
    # for hot in hot_dict:
    #     hot_url = hot.xpath('@href')[0]
    #     hot_code = hot_url.split('/')[-1]
    #     hot_name = hot.xpath('span/text()')[0]
    #     hot_dict[hot_code] = hot_name
    # 收集区域字典
    region_list = tree.xpath('//*[@id="region-nav"]/a')
    region_dict = {}
    for region in region_list:
        region_url = region.xpath('@href')[0]
        # 区域
        region_name = region.xpath('span/text()')[0]
        response = request_get(region_url, ip)
        if not response:
            print(region_url, '-' * 100)
            continue
        html_2 = response.text
        tree_2 = etree.HTML(html_2)
        try:
            street_list = tree_2.xpath('//div[@id="region-nav-sub"]/a/span/text()')[1:]
            if not street_list:
                data = {
                    'city': city,
                    'region': region_name,
                    'street': None
                }
                print(data)
                coll.insert_one(data)
            for street in street_list:
                data = {
                    'city': city,
                    'region': region_name,
                    'street': street
                }
                print(data)
                coll.insert_one(data)
        except Exception as e:
            data = {
                'city': city,
                'region': region_name,
                'street': None
            }
            print(data)
            coll.insert_one(data)
