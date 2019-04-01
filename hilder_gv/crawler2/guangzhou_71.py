import re
import requests
from backup.crawler_base import Crawler
from html.parser import HTMLParser

html_parser = HTMLParser()


class Guangzhou(Crawler):
    def __init__(self):
        self.url = 'http://www.gzcc.gov.cn/laho/ProjectSearch.aspx'
        self.source_url = 'http://www.gzcc.gov.cn'

    def start_crawler(self):
        page = self.get_page()
        print(page)
        for i in range(1, page + 1):
            url = 'http://www.gzcc.gov.cn/laho/ProjectSearch.aspx?page=' + str(i)
            html = requests.get(url).content.decode()
            for k in re.findall('<tr>.*?align="center"><A target="_blank" href="(.*?)">', html, re.S | re.M):
                comm_detail_url = self.source_url + html_parser.unescape(k).strip()
                comm_detail_html = requests.get(comm_detail_url).content.decode()

    def get_page(self):
        res = requests.get(url=self.url)
        # print(res.content.decode())
        html = res.content.decode()
        page = re.search('/共(.*?)页', html, re.M | re.S).group(1)
        return int(page)
