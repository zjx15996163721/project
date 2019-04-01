import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
import pika
import json
import threading
log = LogHandler('58tongcheng')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['gv_merge']


class TongChengConsumer:

    def __init__(self):
        self.headers = {
            'upgrade-insecure-requests': '1',
            'cookie': 'f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; f=n; commontopbar_new_city_info=2%7C%E4%B8%8A%E6%B5%B7%7Csh; commontopbar_ipcity=changningx%7C%E9%95%BF%E5%AE%81%7C0; id58=c5/nn1wXQ3A0wzemGmI5Ag==; 58tj_uuid=ac20c541-e164-40e1-9718-be72a9452a47; new_uv=1; utm_source=; spm=; init_refer=; als=0; xxzl_deviceid=1JOCn9ahzkV496HWqiDmLtPpyMp%2FqLfDRox4ARmC2AAe3nOLYPtz7J6sLdUh2EYu; new_session=0; f=n; JSESSIONID=54D1B5AD360417F8F11B455DB234A22B; Hm_lvt_ae019ebe194212c4486d09f377276a77=1545037907,1545037957,1545037977,1545038822; duibiId=; Hm_lpvt_ae019ebe194212c4486d09f377276a77=1545040844; xzfzqtoken=vvdvRNqvfO8hPQ%2Bm58R0uy2w74j8E4SAW9z6iSlRNtz1Kyny7dnQ2tU5%2BxbYsSiHin35brBb%2F%2FeSODvMgkQULA%3D%3D',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='58tongcheng')

    def final_parse(self, url):
        print(url)
        try:
            r = requests.get(url=url, headers=self.headers, proxies=p)
        except Exception as e:
            log.error(e)
            self.channel.basic_publish(exchange='',
                                       routing_key='58tongcheng',
                                       body=json.dumps(url))
            log.info('放队列 {}'.format(url))
            return
        tree = etree.HTML(r.text)
        try:
            city = tree.xpath('/html/body/div[2]/div[2]/a[3]/text()')[0].replace('小区', '')
        except:
            return
        try:
            region = tree.xpath('/html/body/div[2]/div[2]/a[4]/text()')[0].replace('小区', '')
        except:
            return
        try:
            name = tree.xpath('/html/body/div[2]/div[3]/span[1]/text()')[0]
        except:
            return
        try:
            household_count_info = re.search('总住户数</td>.*?>(.*?)</td>', r.text, re.S | re.M).group(1)
            household_count = re.search('(\d+)', household_count_info, re.S | re.M).group(1)
        except:
            household_count = None
        try:
            estate_charge = re.search('物业费用</td>.*?>(.*?)元', r.text, re.S | re.M).group(1).replace(' ', '').replace('\n', '')
        except:
            estate_charge = None
        try:
            address = re.search('详细地址</td>.*?>(.*?)</td>', r.text, re.S | re.M).group(1).replace(' ', '').replace('\n', '')
        except:
            address = None
        try:
            complete_time = re.search('建筑年代</td>.*?>(.*?)年', r.text, re.S | re.M).group(1).replace(' ', '').replace('\n', '')
        except:
            complete_time = None
        data = {
            'source': '58tongcheng',
            'city': city,
            'region': region,
            'district_name': name,
            'complete_time': complete_time,
            'household_count': household_count,
            'estate_charge': estate_charge,
            'address': address,
            'estate_type2': '普通住宅',
        }
        if not crawler_collection.find_one({'source': '58tongcheng', 'city': city, 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}):
            crawler_collection.insert_one(data)
            log.info('插入一条数据{}'.format(data))
        else:
            crawler_collection.find_one_and_update({'source': '58tongcheng', 'city': city, 'region': region, 'district_name': name,
                                            'household_count': household_count, 'estate_charge': estate_charge,
                                            'address': address}, {'$set': {'complete_time': complete_time}})
            log.info('更新竣工时间{}'.format(complete_time))

    def callback(self, ch, method, properties, body):
        url = json.loads(body.decode())
        self.final_parse(url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='58tongcheng')
        self.channel.start_consuming()


if __name__ == '__main__':
    for i in range(80):
        tongcheng = TongChengConsumer()
        threading.Thread(target=tongcheng.start_consuming).start()


