import requests
import pika
import json
from lxml import etree
from lib.log import LogHandler
from retry import retry
import re

log = LogHandler('anjuke_producer_detail_url')

class VerifyError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

class AnjukeProducer:
    def  __init__(self,proxies):
        self.proxies = proxies
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='114.80.150.196',
            port=5673,
            heartbeat=0
        ))
        self.detail_channel = self.connection.channel()
        self.channel = self.connection.channel()
        # 以下队列中存放写字楼详情页的url
        self.detail_channel.queue_declare(queue='loupan_office_detail_url', durable=True)
        self.detail_channel.queue_declare(queue='new_office_detail_url', durable=True)
        self.channel.queue_declare(queue='anjuke_city_url_list', durable=True)
    def start_consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            self.callback,
            queue='anjuke_city_url_list'
        )
        self.channel.start_consuming()

    def callback(self,ch,method,properties,body):
        city_url = json.loads(body.decode())
        self.send_city_url(city_url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    @retry(logger=log,delay=2)
    def send_city_url(self,city_url):
        """
        :param city_url: https://shanghai.anjuke.com/
        :return:
        """
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res = requests.get(city_url,headers=self.headers,proxies=self.proxies)
        print(city_url)
        text = res.text
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in text:
            raise VerifyError('返回结果不是想要的结果')
        if '商铺写字楼' not in text:
            return
        else:
            if '访问验证-安居客' in text:
                raise VerifyError('出现滑块验证码')
            city_res = etree.HTML(res.content.decode())
            a_list = city_res.xpath('//div[@id="glbNavigation"]/div/ul/li/a')
            for a in a_list:
                name = a.xpath('text()')[0]
                if name == '商铺写字楼':
                    main_url = a.xpath('@href')[0]
                    print('商铺写字楼',main_url)
                    self.send_list_url(main_url)

    @retry(logger=log,delay=2)
    def send_list_url(self,main_url):
        """
        :param main_url:https://sh.xzl.anjuke.com/zu
        :return:解析出来写字楼列表页
        """
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        try:
            res = requests.get(main_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('该网站请求不到{}'.format(main_url))
            return
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res.text:
            raise VerifyError('返回结果不是想要的结果')
        list_res = etree.HTML(res.text)
        office_a_list = list_res.xpath('//div[@class="nav header-center clearfix"]/ul/li/a')
        if len(office_a_list) ==0:
            raise VerifyError('标签列表为空，出现滑块验证码')
        else:
            for a in office_a_list:
                office_name = a.xpath('text()')[0]
                if office_name == '写字楼新盘':
                    print(office_name)
                    #https://sh.fang.anjuke.com/xzl/all/p4_w5/
                    #base_new_url:https://sh.fang.anjuke.com/xzl/all/w5/
                    base_new_url = a.xpath('@href')[0]
                    print(base_new_url)
                    self.xzl_new_base(base_new_url)
                if office_name == '楼盘':
                    print(office_name)
                    #base_loupan_url:https://sh.xzl.anjuke.com/loupan/
                    #页数：https://sh.xzl.anjuke.com/loupan/p120/
                    base_loupan_url = a.xpath('@href')[0]
                    print(base_loupan_url)
                    result = re.search('(https.*com)', base_loupan_url)
                    if result:
                        base_url = result.group(1)
                        print(base_url)
                        for x in range(1, 200):
                            loupan_url = base_loupan_url + 'p' + str(x) + '/'
                            print(loupan_url)
                            result = self.parse_loupan(loupan_url,base_url)
                            if not result:
                                break

    @retry(logger=log,delay=2)
    def xzl_new_base(self,base_new_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_new = requests.get(base_new_url, headers=self.headers, proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res_new.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res_new.text:
            raise VerifyError('出现滑块验证码')
        html_new = etree.HTML(res_new.text)
        total_num = html_new.xpath('//div[@class="key-sort"]/div[@class="sort-condi"]/span[@class="result"]/em/text()')
        if len(total_num)>0:
            total_num = total_num[0]
        else:
            total_num = 0
        total_page = int(int(total_num) / 50) + 1
        print(total_page)
        for x in range(1, total_page + 1):
            result = re.search('(.*?all/)', base_new_url).group(1)
            new_url = result + 'p' + str(x) + '_w5/'
            print(new_url)
            res_new_page = self.xzl_new_page(new_url)
            self.parse_new(res_new_page)

    @retry(logger=log,delay=2)
    def xzl_new_page(self,new_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_new_page = requests.get(new_url, headers=self.headers, proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res_new_page.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res_new_page.text:
            raise VerifyError('出现滑块验证码')
        else:
            return res_new_page

    def parse_new(self,res_new_page):
        html_new = etree.HTML(res_new_page.text)
        detail_urls = html_new.xpath('//div[@class="list-results"]/div[@class="key-list"]/div/@data-link')
        self.detail_channel.basic_publish(
            exchange='',
            routing_key='new_office_detail_url',
            body=json.dumps(detail_urls),
            properties=pika.BasicProperties(delivery_mode=2,)
            )
        print('将新盘的一页放入到队列中{}'.format(res_new_page.url))


    @retry(logger=log, delay=2)
    def parse_loupan(self, loupan_url,base_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_loupan = requests.get(loupan_url, headers=self.headers, proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res_loupan.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res_loupan.text:
            raise VerifyError('出现滑块验证码')
        html_loupan = etree.HTML(res_loupan.text)
        none_tag = html_loupan.xpath('//div[@class="layout"]/div[@id="list-content"]/div[@class="comhead"]/div[@class="noresult-tips"]/text()')
        print(none_tag)
        if len(none_tag) > 0:
            log.error('{}没有更多搜索结果了'.format(res_loupan.url))
            return False
        else:
            # 获取每一个写字楼详情页的url,并将每一页所有的写字楼链接放入到一个列表中。并将其放入到队列中
            #detail_url :/loupan/382271
            detail_urls = html_loupan.xpath('//div[@class="layout"]/div[@id="list-content"]/div[@class="list-item"]/@link')
            if len(detail_urls) == 0:
                print(res_loupan.text)
                return False
            detail_dict = {}
            detail_dict[base_url] = detail_urls
            print(detail_dict)
            self.detail_channel.basic_publish(
                exchange='',
                routing_key='loupan_office_detail_url',
                body=json.dumps(detail_dict),
                properties=pika.BasicProperties(delivery_mode=2, )
            )
            print('将楼盘的一页放入到队列中{}'.format(loupan_url))
            return True


if __name__ == '__main__':
    AnjukeProducer(proxies=next(p)).start_consume()












