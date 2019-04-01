import requests
from lxml import etree
import re
from retry import retry
import json


def decode(result, encode):
    if encode:
        html_content = result.content.decode(encode)
    else:
        html_content = result.content.decode()
    return html_content


@retry(tries=3)
def do_request(url, method, headers, analyzer, encode):
    """

    :param url:
    :param method:'get', 'post'
    :return: html_tree
    """
    try:
        if method is 'get':
            result = requests.get(url, headers=headers, )
            if analyzer is 'xpath':
                html_tree = decode(result, encode)
                return etree.HTML(html_tree)
            else:
                html_tree = decode(result, encode)
                return html_tree
        else:
            # todo post
            pass
    except Exception as e:
        print(e)
        print('连接错误')
        raise


class AllListUrl:
    """
    根据首页获取全部页数
    :return int(page_num)
    """

    def __init__(self, page_count_rule, first_page_url=None, encode=None, request_method=None, headers=None,
                 analyzer_type='regex', ):
        """

        :param page_count_rule: 页码正则表达式/xpath的规则
        :param first_page_url: url
        :param encode: 'gbk'
        :param request_method: 'get', 'post'
        :param headers: http requests header
        """
        self.first_page_url = first_page_url
        self.encode = encode
        self.method = request_method
        self.analyzer = analyzer_type
        self.headers = headers
        self.page_count_rule = page_count_rule

    def get_page_count(self, ):
        html_ = do_request(self.first_page_url, self.method, self.headers, self.analyzer, self.encode)
        if self.analyzer is 'xpath':
            print('开始xpath')
            result = html_.xpath(self.page_count_rule)[0]
            print(int(result.text))
            return int(result.text)
        else:
            print('开始正则')
            result = re.search(self.page_count_rule, html_, re.M | re.S).group(1)
            print(int(result))
            return int(result)


if __name__ == '__main__':
    h = {
        'Cache-Control': "no-cache",
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
    }

    url = 'http://www.gafdc.cn/newhouse/houselist.aspx?hou=0-0-0-0-0-0-&page=1'
    b = AllListUrl(first_page_url=url,
                   request_method='get',
                   analyzer_type='regex',
                   encode='utf-8',
                   page_count_rule='pageCount = (.*?);',
                   )
    b.get_page_count()
