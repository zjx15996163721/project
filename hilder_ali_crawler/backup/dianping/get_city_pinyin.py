import requests
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

count = 0


def get_city_list():
    city_url = 'http://www.dianping.com/citylist'
    response = requests.get(city_url, headers=headers)
    html = response.text
    tree = etree.HTML(html)
    city_tree = tree.xpath('//div[@class="findHeight"]/a[@class="link onecity"]')
    for i in city_tree:
        city = i.xpath('text()')[0]
        url = i.xpath('@href')[0]
        pinyin = url.split('/')[-1]
        data = {
            'city': city,
            'pinyin': pinyin
        }
        print(data)
        global count
        count += 1
        print(count)


if __name__ == '__main__':
    get_city_list()
