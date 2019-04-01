import requests
from bs4 import BeautifulSoup
from backup.fangtianxia.city import get_All_City
from backup.fangtianxia.articletwo import getarticle2
from backup.fangtianxia.articleone import getarticle1
from lib.bloom_filter import BloomFilter
from article import Article
from article_img.qiniu_fetch import qiniufetch
import time
import yaml
import datetime
from lib.log import LogHandler


setting = yaml.load(open('config_local.yaml'))
article = Article('房天下')
log = LogHandler("fangtianxia")

class Fangtianxia(object):
    def __init__(self):
        self.bf = BloomFilter(host=setting['redies_host'],
                              port=setting['redis_port'],
                              key='article_toutiao_test',
                              blockNum=1,
                              db=0, )
    #今日头条
    def todaynews(self, url):
        try:
            response = requests.get(url)
            response.encoding = 'GBK'
            html = BeautifulSoup(response.text, 'lxml')
            # 今日头条第一个链接
            link1 = html.select('#newsid_D02_02 > a')[0].get('href')                                #今日头条第一个链接 (图片)
            link2 = html.select('#newsid_D02_02 > a > img')[0].get('src')                           #今日头条第一个图片地址

            # 抓取字段
            main1 = html.select('.news-main')[0].text.strip('[详情]').strip()                       #今日头条第一个链接   概述
            zan1 = html.select('.like')[0].text.strip('（').strip('）').strip()                     #今日头条第一个链接   点赞量
            # 今日头条第二个链接
            link5 = html.select('#newsid_D02_03 > a')[0].get('href')                                #今日头条第二条链接(图片)
            link6 = html.select('#newsid_D02_03 > a > img')[0].get('src')                           #今日头条第二个图片地址

            # 抓取字段
            main2 =html.select('.news-main')[1].text.strip('[详情]').strip()                        #今日头条第二个链接   概述
            zan2 = html.select('.like')[1].text.strip().strip('（').strip('）')                     #今日头条第二个链接   点赞量
            #分类
            category = html.select('.xw-tit')[0].text
            if self.bf.is_contains(link1):
                log.info('bloom_filter已经存在{}'.format(link1))
            else:
                self.bf.insert(link1)
                log.info('bloom_filter不存在，插入新的url:{}'.format(link1))
                file_name = link2
                link2 = qiniufetch(link2, file_name)

                #第一个链接添加字段
                if 'open' in link1:
                    list1 = getarticle2(link1)         #调用方法，获取字段
                    article.title = list1[0]
                    article.source_detail = list1[1]
                    article.post_time = list1[2]
                    article.body = list1[3]
                    article.tag = list1[4]
                    article.city = list1[5]
                    article.title_img = link2
                    article.desc = main1
                    article.like_count = zan1
                    article.url = link1
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                elif 'open' not in link1:
                    list2 = getarticle1(link1)
                    article.title = list2[0]
                    article.source_detail = list2[1]
                    article.post_time = list2[2]
                    article.body = list2[3]
                    article.tag = list2[4]
                    article.author = list2[6]
                    article.city = list2[7]
                    article.title_img = link2
                    article.desc = main1
                    article.like_count = zan1
                    article.url = link1
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                else:
                    return None

            if self.bf.is_contains(link5):
                log.info('bloom_filter已经存在{}'.format(link5))
            else:
                self.bf.insert(link5)
                log.info('bloom_filter不存在，插入新的url:{}'.format(link5))
                file_name = link6
                link6 = qiniufetch(link6, file_name)
                #第二个链接添加字段
                if 'open' in link5:
                    list3 = getarticle2(link5)         #调用方法，获取字段
                    article.title = list3[0]
                    article.source_detail = list3[1]
                    article.post_time = list3[2]
                    article.body = list3[3]
                    article.tag = list3[4]
                    article.city = list3[5]
                    article.title_img = link6
                    article.desc = main2
                    article.like_count = zan2
                    article.url = link5
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                elif 'open' not in link5:
                    list4 = getarticle1(link5)
                    article.title = list4[0]
                    article.source_detail = list4[1]
                    article.post_time = list4[2]
                    article.body = list4[3]
                    article.tag = list4[4]
                    article.author = list4[6]
                    article.city = list4[7]
                    article.title_img = link6
                    article.desc = main2
                    article.like_count = zan2
                    article.url = link5
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                else:
                    return None
        except Exception as e:
            log.error(e)
    #房产要闻
    def House_News(self, url):
        try:
            response = requests.get(url)
            response.encoding = 'GBK'
            html = BeautifulSoup(response.text, 'lxml')
            # 房产要闻 第一个链接
            link1 = html.select('#newsid_D02_04 > a')[0].get('href')                                #房产要闻 第一个链接 (图片)
            link2 = html.select('#newsid_D02_04 > a > img')[0].get('src')                           #房产要闻第一个图片地址

            #抓取字段
            main1 = html.select('.news-main')[2].text.strip('[详情]').strip()                       #房产要闻第一个链接   概述
            zan1 = html.select('.like')[2].text.strip('（').strip('）').strip()                     #房产要闻第一个链接   点赞量
            # 房产要闻 第二个链接
            link5 = html.select('#newsid_D02_04 > a')[1].get('href')                                #房产要闻 第二个链接 (图片)
            link6 = html.select('#newsid_D02_04 > a > img')[1].get('src')                           #房产要闻第二个图片地址

            #抓取字段
            main2 = html.select('.news-main')[3].text.strip('[详情]').strip()                       #房产要闻第一个链接   概述
            zan2 = html.select('.like')[3].text.strip('（').strip('）').strip()                     #房产要闻第一个链接   点赞量
            #分类
            category = html.select('.xw-tit')[1].text
            if self.bf.is_contains(link1):
                log.info('bloom_filter已经存在{}'.format(link1))
            else:
                self.bf.insert(link1)
                log.info('bloom_filter不存在，插入新的url:{}'.format(link1))
                file_name = link2
                link2 = qiniufetch(link2, file_name)

                # 第一个链接添加字段
                if 'open' in link1:
                    list1 = getarticle2(link1)  # 调用方法，获取字段
                    article.title = list1[0]
                    article.source_detail = list1[1]
                    article.post_time = list1[2]
                    article.body = list1[3]
                    article.tag = list1[4]
                    article.city = list1[5]
                    article.title_img = link2
                    article.desc = main1
                    article.like_count = zan1
                    article.url = link1
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                elif 'open' not in link1:
                    list2 = getarticle1(link1)
                    article.title = list2[0]
                    article.source_detail = list2[1]
                    article.post_time = list2[2]
                    article.body = list2[3]
                    article.tag = list2[4]
                    article.author = list2[6]
                    article.city = list2[7]
                    article.title_img = link2
                    article.desc = main1
                    article.like_count = zan1
                    article.url = link1
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                else:
                    return None
            if self.bf.is_contains(link5):
                log.info('bloom_filter已经存在{}'.format(link5))
            else:
                self.bf.insert(link5)
                log.info('bloom_filter不存在，插入新的url:{}'.format(link5))
                file_name = link6
                link6 = qiniufetch(link6, file_name)
                # 第二个链接添加字段
                if 'open' in link5:
                    list3 = getarticle2(link5)  # 调用方法，获取字段
                    article.title = list3[0]
                    article.source_detail = list3[1]
                    article.post_time = list3[2]
                    article.body = list3[3]
                    article.tag = list3[4]
                    article.city = list3[5]
                    article.title_img = link6
                    article.desc = main2
                    article.like_count = zan2
                    article.url = link5
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                elif 'open' not in link5:
                    list4 = getarticle1(link5)
                    article.title = list4[0]
                    article.source_detail = list4[1]
                    article.post_time = list4[2]
                    article.body = list4[3]
                    article.tag = list4[4]
                    article.author = list4[6]
                    article.city = list4[7]
                    article.title_img = link6
                    article.desc = main2
                    article.like_count = zan2
                    article.url = link5
                    article.category = category
                    article.crawler_time = datetime.datetime.now()
                    article.insert_db()
                else:
                    return None
        except Exception as e:
            log.error(e)
    #本地热点
    def localhot(self, url):
        try:
            response = requests.get(url)
            response.encoding = 'GBK'
            html = BeautifulSoup(response.text, 'lxml')
            piece = html.select('.left-part > dl')[2]
            category = piece.select('dt > h2')[0].text
            eachpiece1 = piece.select('dd > div')
            eachpiece2 = piece.select('dd > ul > li')
            for i in eachpiece1:
                link = i.select('.news-content > h3 > a')[0].get('href')
                main = i.select('.news-content > p')[0].text.strip().strip('[详情]')
                imglink = i.select('a > .news-img')[0].get('src')

                if self.bf.is_contains(link):
                    log.info('bloom_filter已经存在{}'.format(link))
                    continue
                else:
                    self.bf.insert(link)
                    log.info('bloom_filter不存在，插入新的url:{}'.format(link))
                    file_name = imglink
                    imglink = qiniufetch(imglink, file_name)
                    if 'open' in link:
                        list1 = getarticle2(link)
                        article.title = list1[0]
                        article.source_detail = list1[1]
                        article.post_time = list1[2]
                        article.body = list1[3]
                        article.tag = list1[4]
                        article.city = list1[5]
                        article.desc = main
                        article.url = link
                        article.title_img = imglink
                        article.category = category
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    elif 'open' not in link:
                        list2 = getarticle1(link)
                        article.title = list2[0]
                        article.source_detail = list2[1]
                        article.post_time = list2[2]
                        article.body = list2[3]
                        article.tag = list2[4]
                        article.author = list2[6]
                        article.city = list2[7]
                        article.desc = main
                        article.url = link
                        article.title_img = imglink
                        article.category = category
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    else:
                        return None
            for j in eachpiece2:
                link = j.select('span > a')[0].get('href')
                if self.bf.is_contains(link):
                    log.info('bloom_filter已经存在{}'.format(link))
                    continue
                else:
                    self.bf.insert(link)
                    log.info('bloom_filter不存在，插入新的url:{}'.format(link))
                    if 'open' in link:
                        list3 = getarticle2(link)
                        article.title = list3[0]
                        article.source_detail = list3[1]
                        article.post_time = list3[2]
                        article.body = list3[3]
                        article.tag = list3[4]
                        article.city = list3[5]
                        article.url = link
                        article.category = category
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    elif 'open' not in link:
                        list4 = getarticle1(link)
                        article.title = list4[0]
                        article.source_detail = list4[1]
                        article.post_time = list4[2]
                        article.body = list4[3]
                        article.tag = list4[4]
                        article.desc = list4[5]
                        article.author = list4[6]
                        article.city = list4[7]
                        article.url = link
                        article.category = category
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    else:
                        return None
        except Exception as e:
            log.error(e)
    #未分类新闻
    def UnfiledNews(self, url):
        try:
            response = requests.get(url)
            response.encoding = 'GBK'
            html = BeautifulSoup(response.text, 'lxml')
            piece = html.select('.left-part > dl')[3]
            eachpiece = piece.select('dd > div')
            for i in eachpiece:
                link = i.select('div > h3 > a')[0].get('href')
                main = i.select('div > .news-main')[0].text.strip().strip('[详情]')
                imglink = i.select('a > .news-img')[0].get('src')

                zan = i.select('.news-content > div > .like')[0].text.strip('（').strip('）')
                if self.bf.is_contains(link):
                    log.info('bloom_filter已经存在{}'.format(link))
                    continue
                else:
                    self.bf.insert(link)
                    log.info('bloom_filter不存在，插入新的url:{}'.format(link))
                    file_name = imglink
                    imglink = qiniufetch(imglink, file_name)
                    if 'open' in link:
                        list1 = getarticle2(link)
                        article.title = list1[0]
                        article.source_detail = list1[1]
                        article.post_time = list1[2]
                        article.body = list1[3]
                        article.tag = list1[4]
                        article.city = list1[5]
                        article.desc = main
                        article.url = link
                        article.title_img = imglink
                        article.like_count = zan
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    elif 'open' not in link:
                        list2 = getarticle1(link)
                        article.title = list2[0]
                        article.source_detail = list2[1]
                        article.post_time = list2[2]
                        article.body = list2[3]
                        article.tag = list2[4]
                        article.author = list2[6]
                        article.city = list2[7]
                        article.desc = main
                        article.url = link
                        article.title_img = imglink
                        article.like_count = zan
                        article.crawler_time = datetime.datetime.now()
                        article.insert_db()
                    else:
                        return None
        except Exception as e:
            log.error(e)
    #列表页链接
    def getlinks(self, url):
        try:
            page = 0
            while page >= 0:
                page = page + 1
                time1 = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                url1 = url.replace('.com/', '.com/gdxw') + '/' + time1 + '/' + str(page) + '.html'
                if url1:
                    headers = {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate',
                            'Accept-Language': 'zh-CN,zh;q=0.9',
                            'Cache-Control': 'max-age=0',
                            'Connection': 'keep-alive'
                            }
                    response = requests.get(url=url1, headers=headers)
                    response.encoding = 'GBK'
                    soup = BeautifulSoup(response.text,'lxml')
                    piece = soup.select('.infoBox-list')[0]
                    eachpiece = piece.select('.infoBox-item')
                    for i in eachpiece:
                        imglink = i.select('.infoBox-img > a')
                        if imglink:
                            imgsrc1 = imglink[0].select('img')[0].get('src')

                            link1 = imglink[0].get('href')
                            if self.bf.is_contains(link1):
                                log.info('bloom_filter已经存在{}'.format(link1))
                                continue
                            else:
                                self.bf.insert(link1)
                                log.info('bloom_filter不存在，插入新的url:{}'.format(link1))
                                file_name = imgsrc1
                                imgsrc1 = qiniufetch(imgsrc1, file_name)
                                if 'open' in link1:
                                    list1 = getarticle2(link1)
                                    article.title = list1[0]
                                    article.source_detail = list1[1]
                                    article.post_time = list1[2]
                                    article.body = list1[3]
                                    article.tag = list1[4]
                                    article.city = list1[5]
                                    article.url = link1
                                    article.title_img = imgsrc1
                                    article.crawler_time = datetime.datetime.now()
                                    article.insert_db()
                                elif 'open' not in link1:
                                    list2 = getarticle1(link1)
                                    article.title = list2[0]
                                    article.source_detail = list2[1]
                                    article.post_time = list2[2]
                                    article.body = list2[3]
                                    article.tag = list2[4]
                                    article.desc = list2[5]
                                    article.author = list2[6]
                                    article.city = list2[7]
                                    article.url = link1
                                    article.title_img = imgsrc1
                                    article.crawler_time = datetime.datetime.now()
                                    article.insert_db()
                                else:
                                    return None
                        else:
                            link2 = i.select('h3 > a')[0].get('href')
                            if self.bf.is_contains(link2):
                                log.info('bloom_filter已经存在{}'.format(link2))
                                continue
                            else:
                                self.bf.insert(link2)
                                log.info('bloom_filter不存在，插入新的url:{}'.format(link2))
                                if 'open' in link2:
                                    list3 = getarticle2(link2)
                                    article.title = list3[0]
                                    article.source_detail = list3[1]
                                    article.post_time = list3[2]
                                    article.body = list3[3]
                                    article.tag = list3[4]
                                    article.city = list3[5]
                                    article.url = link2
                                    article.crawler_time = datetime.datetime.now()
                                    article.insert_db()
                                elif 'open' not in link2:
                                    list4 = getarticle1(link2)
                                    article.title = list4[0]
                                    article.source_detail = list4[1]
                                    article.post_time = list4[2]
                                    article.body = list4[3]
                                    article.tag = list4[4]
                                    article.desc = list4[5]
                                    article.author = list4[6]
                                    article.city = list4[7]
                                    article.url = link2
                                    article.crawler_time = datetime.datetime.now()
                                    article.insert_db()
                                else:
                                    return None
                else:
                    break
        except Exception as e:
            log.error(e)
def fangtianxia_start():
    list1 = get_All_City()
    fangtianxia = Fangtianxia()
    for url in list1:
        fangtianxia.todaynews(url)
        fangtianxia.House_News(url)
        fangtianxia.localhot(url)
        fangtianxia.UnfiledNews(url)
        fangtianxia.getlinks(url)







