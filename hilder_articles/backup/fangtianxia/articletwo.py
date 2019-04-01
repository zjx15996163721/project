import requests
from bs4 import BeautifulSoup
from article_img.image_replace import ImageReplace
import random

#第二种文章
def getarticle2(url):
    try:
        proxies = [{"http": "http://192.168.0.96:3234"},
                   {"http": "http://192.168.0.93:3234"},
                   {"http": "http://192.168.0.90:3234"},
                   {"http": "http://192.168.0.94:3234"},
                   {"http": "http://192.168.0.98:3234"},
                   {"http": "http://192.168.0.99:3234"},
                   {"http": "http://192.168.0.100:3234"},
                   {"http": "http://192.168.0.101:3234"},
                   {"http": "http://192.168.0.102:3234"},
                   {"http": "http://192.168.0.103:3234"}, ]
        while True:
            try:
                response = requests.get(url=url, proxies=proxies[random.randint(0, 9)])
                break
            except Exception as e:
                print(e)
        response.encoding = 'GBK'
        soup = BeautifulSoup(response.text,'lxml')

        title = soup.select('.news-cont > .news-title')[0].text                         #标题
        source = soup.select('#xfopen_B01_01')[1].text                                  #来源
        time = soup.select('.comment > span')[2].text                                   #时间
        content = soup.select('.news-text')[0]
        content = content.prettify()
        img_replace = ImageReplace()
        con = img_replace.image_download(content)                                       #内容
        tags = soup.select('#xfopen_B01_11')
        city = soup.select('.s4Box > a')[0].text
        L = []                                                                          #L为所有的标签
        for i in tags:
            tagList = i.text
            L.append(tagList)
        data = [title, source, time, con, L, city]
        return data
    except Exception as e:
        print(e)
# url = 'http://news.sh.fang.com/open/28468149.html'
# getarticle2(url)




