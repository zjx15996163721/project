"""
    不是拍卖网站，不用管这个文件
    rmfysszc的获取区域信息，并入mysql库
"""
import requests
from lxml import etree
from sql_mysql import insert_type, CityAuction

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

data_print = {}
source = 'rmfysszc'

start_url = 'http://www1.rmfysszc.gov.cn/projects.shtml?dh=3&gpstate=1&wsbm_slt=1'
response = requests.get(start_url, headers=headers)
html = response.content.decode()
tree = etree.HTML(html)
value_list = tree.xpath('//select[@id="city"]/option')[1:]
for i in value_list:
    id_1 = i.xpath('@value')[0]
    name_pro = i.xpath('text()')[0]
    data = {'id': id_1}
    second_url = 'http://www1.rmfysszc.gov.cn/GetCity.shtml'
    res = requests.post(url=second_url, data=data, headers=headers)
    html_2 = res.text
    tree_2 = etree.HTML(html_2)
    value_list_2 = tree_2.xpath('//option')
    for j in value_list_2:
        id_2 = j.xpath('@value')
        name_city = j.xpath('text()')[0]
        data_2 = {'id': id_2}
        res_2 = requests.post(url=second_url, data=data_2, headers=headers)
        html_3 = res_2.text
        tree_3 = etree.HTML(html_3)
        value_list_3 = tree_3.xpath('//option/text()')[1:]
        for k in value_list_3:
            if k == '市辖区':
                continue
            print(name_pro, name_city, k)
            new_user = CityAuction(code=k, province=name_pro, city=name_city, region=k, source=source)
            insert_type(new_user, CityAuction)
