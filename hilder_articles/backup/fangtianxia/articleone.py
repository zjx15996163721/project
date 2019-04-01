import requests
from bs4 import BeautifulSoup
from article_img.image_replace import ImageReplace
import random
#第一种文章
def getarticle1(url):
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
        soup = BeautifulSoup(response.text, 'lxml')

        title = soup.select('.news-detail-content > .news-title')[0].text.strip()          #标题
        allsource = soup.select('.assis-title')[0].text.strip().split('\n')
        source1 = allsource[0].strip('\r').split('\xa0')
        source = source1[0]                                                                #来源
        author = source1[2].strip('作者：')                                                #作者
        time = allsource[1].strip().strip('\t')                                            #时间
        content = soup.select('.news-detail-content')[0]
        content = content.prettify()
        img_replace = ImageReplace()
        con = img_replace.image_download(content)                                         #内容
        tags = soup.find_all('span', 'lab-span')
        summery = soup.select('.news-summery')[0].text.strip('[摘要]').strip()             #概述
        city = soup.select('.s4Box > a')[0].text                                           #城市
        L = []                                                                             #L为所有的标签
        for i in tags:
            tagList = i.text
            L.append(tagList)
        data = [title, source, time, con, L, summery, author, city]
        return data
    except Exception as e:
        print(e)

# url = 'http://news.sh.fang.com/2018-05-11/28432687.htm'
# getarticle1(url)



