import requests
from lxml import etree
import re
from retry import retry
import json
from lib.rabbitmq import Rabbit
import yaml

setting = yaml.load(open('config_local.yaml'))


def decode(result, encode):
    """
    html编码
    :param result:
    :param encode:
    :return: html.decode()
    """
    if encode:
        html_content = result.content.decode(encode)
    else:
        html_content = result.content.decode()
    return html_content


def get_html_dom(html_str, ):
    """
    获取html对象
    :param html_str:
    :return: xpath html 对象
    """
    return etree.HTML(html_str)


@retry(tries=3)
def do_request(url, request_type, headers, encode, post_data=None):
    """

    :param url
    :param request_type:'get', 'post'
    :param headers
    :param encode
    :return: html_tree
    """
    try:
        if request_type is 'get':
            result = requests.get(url, headers=headers, timeout=10)
            html_str = decode(result, encode)
            return html_str
        else:
            result = requests.post(url, data=post_data, headers=headers, timeout=10)
            html_str = decode(result, encode)
            return html_str
    except Exception as e:
        print(e)
        print('连接错误')
        raise


class ProducerListUrl:
    """
    根据列表页获取详情页的url
    """

    def __init__(self, page_url, analyzer_rules_dict=None, current_url_rule=None, encode=None,
                 request_type='get', headers=None, post_data=None, analyzer_type='regex', ):
        """
        :param list_page_url: 必填，列表页url ,必须是数组
        ['www.google.com', 'www.github.com']
        :param analyzer_rules_dict: 解析表达式,必须是数组
        [{'co_build_size': None, 'co_owner': None, 'co_build_type': None, 'co_build_end_time': None, 'co_green': None,}]
        :param current_url_rule: 获取当前页面的url的正则表达式/xpath
        :param encode: 编码方式：get，post
        :param request_type: 默认get,可选get, post
        :param headers: requests header {  'Cache-Control': "no-cache','User-Agent':'safari', }
        :param analyzer_type: 默认未正则表达式
        """
        self.page_url = page_url
        self.encode = encode
        self.request_type = request_type
        self.headers = headers
        self.analyzer_type = analyzer_type
        self.current_url_rule = current_url_rule
        self.analyzer_rules_dict = analyzer_rules_dict
        self.post_data = post_data

    def get_list_page_url(self, html_str):
        # 判断解析方式
        url_list = []
        if self.analyzer_type is 'regex':
            # 正则表达式
            print('开始正则表达式获取当前的页面url')
            regex_url_list = re.findall(self.current_url_rule, html_str, re.M | re.S)
            print(len(regex_url_list))
            for url in regex_url_list:
                print(url)
                url_list.append(url)
        else:
            # xpath
            html_tree = get_html_dom(html_str)
            xpath_url_list = html_tree.xpath(self.current_url_rule)
            print(len(xpath_url_list))
            for url in xpath_url_list:
                # print(url)
                url_list.append(url)
        # 解析page_list获取数组返回
        # print(url_list)
        return url_list

    def get_current_page_url(self):
        """
        本方法仅仅返回当前页面的url，不放入队列
        :return:
        """
        if not self.current_url_rule:
            print('缺少参数current_url_rule')
            return
        try:
            html_str = do_request(self.page_url, self.request_type, self.headers, self.encode)
            current_page_list_url = self.get_list_page_url(html_str)
            return current_page_list_url
        except Exception as e:
            print(self.page_url, e)

    def get_details(self):
        """
        把网页放入队列
        如果有list_page_url，返回url列表
        :return:
        """
        r = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'])
        channel = r.get_channel()
        channel.queue_declare(queue='hilder_gv')

        try:
            html_str = do_request(self.page_url, self.request_type, self.headers, self.encode)
            body = {'html': html_str,
                    'analyzer_type': self.analyzer_type,
                    'analyzer_rules_dict': self.analyzer_rules_dict,
                    }
            # 放入队列 json.dumps(body)
            channel.basic_publish(exchange='',
                                  routing_key='hilder_gv',
                                  body=json.dumps(body))
            r.connection.close()
            # print(json.dumps(body))
            print('已经放入队列')
            if self.current_url_rule:
                current_page_list_url = self.get_current_page_url()
                return current_page_list_url
        except Exception as e:
            print(self.page_url, e)


if __name__ == '__main__':
    # list_url = ['http://www.czfdc.gov.cn/spf/gs.php']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    while True:
        page_url = 'http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/BeianDetail.aspx?id=4262&vc=525be7ae'
        from backup.comm_info import Comm

        c = Comm('123')
        c.co_name = '//*[@id="content_1"]/div[3]/text()'
        data_list = {
            'comm': c.to_dict()
        }
        # current_url_rule = 'align="center".*?target="_blank"(.*?)target="_blank"'
        g = ProducerListUrl(page_url=page_url, request_type='get', encode='utf-8',
                            headers=headers,
                            analyzer_rules_dict=data_list, analyzer_type='xpath', )
        g.get_details()
