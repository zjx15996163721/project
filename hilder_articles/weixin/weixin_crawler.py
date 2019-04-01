import requests
import re
import random
from article import Article
from article_img.image_replace import ImageReplace
from lxml import etree
import datetime
from lib.bloom_filter import BloomFilter
import yaml
from lib.log import LogHandler

log = LogHandler("weixin")
setting = yaml.load(open('config_local.yaml'))

url_dict = {
    'http://weixin.sogou.com/weixin?type=1&s_from=input&query=上海中原研究院':'上海中原研究院',
    'http://weixin.sogou.com/weixin?type=1&s_from=input&query=真叫卢俊':'真叫卢俊',
    'http://weixin.sogou.com/weixin?type=1&s_from=input&query=米宅米宅':'米宅米宅',
    'http://weixin.sogou.com/weixin?type=1&s_from=input&query=上海房地产观察':'上海房地产观察',
}
headers={
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}

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

bf = BloomFilter(host=setting['redies_host'],
                              port=setting['redis_port'],
                              key='article_toutiao_test',
                              blockNum=1,
                              db=0, )

def weixin_start():
    for item in url_dict.items():
        url = item[0]
        source_detail = item[1]
        sougou_res = requests.get(url,headers=headers,)
        sougou_html = etree.HTML(sougou_res.text)
        weixin_url = sougou_html.xpath("//p[@class='tit']/a/@href")[0]
        res = requests.get(weixin_url,headers=headers,)
        try:
            msg = re.search('var msgList = (.*?)seajs.use',res.text,re.S|re.M).group(1)
        except:
            continue
        content_urllist = re.findall('content_url":"(.*?)"',msg)
        for content_url in content_urllist:
            article_url = content_url.replace('amp;','')
            article_parse(article_url,source_detail)

def article_parse(article_url,source_detail):
    while True:
        try:
            url = 'https://mp.weixin.qq.com' + article_url
            proxy = proxies[random.randint(0,9)]
            res = requests.get(url,headers=headers,proxies=proxy)
            break
        except Exception as e:
            log.error(e)
    html = etree.HTML(res.text)
    try:

        title = html.xpath("//h2[@id='activity-name']/text()")[0]
        if len(title.strip()) == 0:
            title = re.search("rich_media_title_ios'>(.*?)</span",res.text).group(1)
        sign = source_detail + title
        if bf.is_contains(sign):  # 过滤详情页
            log.info('bloom_filter已经存在{}'.format(sign))
            return
        else:
            bf.insert(sign)
            log.info('bloom_filter不存在，插入新的url:{}'.format(sign))

        try:
            author = re.search('作者&nbsp;(.*?)</',res.text).group(1)
        except:
            author = None
        try:
            post_time = re.findall('publish_time = "(.*?)"',res.text)[0]
        except:
            post_time = None
        content = html.xpath("//div[@class='rich_media_content ']")[0]
        body = etree.tounicode(content)
    except Exception as e:
        log.error('文章解析失败')
        return

    img_change = ImageReplace()
    readable_body = img_change.image_download(body)
    article = Article('微信公众号')
    article.title = title
    article.author = author
    article.source_detail = source_detail
    article.body = readable_body
    article.post_time = post_time
    article.crawler_time = datetime.datetime.now()
    article.insert_db()
    log.info("{}文章已入库".format('微信'))


if __name__ == '__main__':
    weixin_start()