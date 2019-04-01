import pika
import yaml
import requests
from lib.proxy_iterator import Proxies
from lib.log import LogHandler
from lxml import etree
import re
import json
from pymongo import MongoClient
log = LogHandler(__name__)
p = Proxies()
setting = yaml.load(open('config_dianping.yaml'))
m = MongoClient(host=setting['mongo']['host'], port=setting['mongo']['port'], username=setting['mongo']['user_name'], password=setting['mongo']['password'])
db = m[setting['mongo']['db_name']]
dianping_all_type_collection = db[setting['mongo']['shop_detail_collection']]
connection = pika.BlockingConnection(pika.ConnectionParameters(host=setting['rabbit']['host'], port=setting['rabbit']['port']))
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')


class ConvertIdRpcServer(object):
    def __init__(self, proxies):
        self.proxies = proxies
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            }

    def convert_id(self, new_body):
        try:
            name = new_body['name']
            matchText = new_body['matchText']
            cityId = new_body['cityId']
            url = 'https://m.dianping.com/shoplist/{}/search?from=m_search&keyword={}{}'.format(cityId, matchText, name)
            print(url)
            try:
                r = requests.get(url=url, headers=self.headers, proxies=self.proxies)
                tree = etree.HTML(r.text)
                shop_link = tree.xpath("//ul[@class='list-search']/li/a/@href")
                if len(shop_link) == 1:
                    shop_id = re.search('//m\.dianping\.com/shop/(\d+)\?from=(.*)', shop_link[0]).group(1)
                    print(shop_id)
                    new_body.update({'id': shop_id})
                    return new_body
                else:
                    for link in shop_link:
                        shop_id = re.search('//m\.dianping\.com/shop/(\d+)\?from=(.*)', link).group(1)
                        print(shop_id)
                        if dianping_all_type_collection.find_one({"id": shop_id}) is None:
                            new_body.update({'id': shop_id})
                            return new_body
                        else:
                            print("已经存在库中")
                            continue
            except Exception as e:
                log.error('请求失败,切换代理={}'.format(url))
                self.proxies = next(p)
        except Exception as e:
            print(e)

    def on_request(self, ch, method, props, body):
        response = self.convert_id(json.loads(body.decode()))
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_request, queue='rpc_queue')
        print("等待RPC请求")
        channel.start_consuming()


if __name__ == '__main__':
    convert_id = ConvertIdRpcServer(next(p))
    convert_id.start_consuming()




