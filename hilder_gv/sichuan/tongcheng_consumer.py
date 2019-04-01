import requests
from lxml import etree
from lib.proxy_iterator import Proxies
from pymongo import MongoClient
import re
from lib.log import LogHandler
import pika
import json
import threading
from retry import retry
log = LogHandler('58tongcheng_consumer')
p = Proxies()
p = p.get_one(proxies_number=7)

m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
crawler_collection = m['hilder_gv']['sichuan']


class TongChengConsumer:

    def __init__(self):
        self.headers = {
            'upgrade-insecure-requests': '1',
            'cookie': 'f=n; commontopbar_new_city_info=102%7C%E6%88%90%E9%83%BD%7Ccd; f=n; commontopbar_new_city_info=102%7C%E6%88%90%E9%83%BD%7Ccd; id58=dbarwVvWv6gwVNEoyu/IPg==; 58tj_uuid=253875e3-6ad5-4dba-9087-f7f30bbaa730; new_uv=1; utm_source=sem-baidu-pc; spm=105916146851.26420796316; init_refer=https%253A%252F%252Fwww.baidu.com%252Fbaidu.php%253Fsc.af0000aF4eAvq9HI8zvj0uhRohNRqby2LrylmoRdGKHccDnOlvS92op8V14PAw_gGsweqGFXZTcU_sOCmzJGIlVk6QgU-2w-OMy9icJXcEfFuZ-rOgvbTeX0_J8raTKGfPF5_hEu7twB6QciWTwyn7KM3vnYFjTsPLGjfo6R517MKU6kaWBV3yVAbGOi8ZsACxXijpMczHi1DXBLXs.Db_jI_wKLk_Y2hrSa9G4mLmFCR_wGY4evTyj5W9s4rh5ZGmo_LUlShE_lIhlEzzI5ub_tIOHkolTrHGsRP5Qa1Gk_EdwnwGCYTrHGsRP5QGHTOKGm9ksJN9h9moLI-hqf0.U1Yk0ZDqPHWPoQ5Z0ZKGm1Ys0ZfqPHWPoQ5Z0A-V5HczPfKM5yF-TZnk0ZNG5yF9pywd0ZKGujYz0APGujYYnj60UgfqnH0kPdtknjD4g1DsnWPxnH0YP-t1PW0k0AVG5H00TMfqrHcY0ANGujYkPjnzg1cknH03g1c3nW0vg1c3nHnzg1cvn1Rsg1cLP1Rsg1c3nHfsg1cLPH030AFG5Hfsn-tznjf0Uynqrj04PWRdnjc1g1Dsnj7xnNtknjFxn0KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0ZwdT1YknHm3PWRzP1b4rHnkP16Yrjn4rfKzug7Y5HDdPjR3njcdPWbknWn0Tv-b5yPhmhwbmWRdnj0snANWrym0mLPV5HcsPjfsPDnkrHTdrH6dPYf0mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0ZGY5H00UyPxuMFEUHYsg1Kxn7tsg100uA78IyF-gLK_my4GuZnqn7tsg1Kxn1nLPHTdn-ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00uMGC5H00uh7Y5H00XMK_Ignqn0K9uAu_myTqnfK_uhnqn0KWThnqn1f4PWR%2526word%253D58%2525E5%252590%25258C%2525E5%25259F%25258E%2526ck%253D8338.4.150.301.177.284.172.308%2526shh%253Dwww.baidu.com%2526sht%253Dbaidu%2526us%253D1.0.1.0.1.301.0%2526bc%253D110101; als=0; new_session=0; f=n; city=cd; 58home=cd; commontopbar_new_city_info=102%7C%E6%88%90%E9%83%BD%7Ccd; commontopbar_ipcity=sh%7C%E4%B8%8A%E6%B5%B7%7C0; xxzl_deviceid=60rEGHEr1bTzTVdjdcSRNSpl7Bx45xYxUFtiEijrCQO6llSidyGLLBn6XztwH9y%2B; wmda_uuid=c196bf0dc5036e661528952d64738430; wmda_new_uuid=1; JSESSIONID=D6E65B7AA1583B691BAC5DF75604B992; wmda_visited_projects=%3B2385390625025%3B6333604277682; duibiId=; wmda_session_id_2385390625025=1545805081498-09ed7c07-9979-bf38; Hm_lvt_ae019ebe194212c4486d09f377276a77=1545802747,1545805123; Hm_lpvt_ae019ebe194212c4486d09f377276a77=1545805123; xzfzqtoken=Wc3Ib5VaBkz66SLt3KXwQk%2FrgiuWlgJ4Rw1hnfPWjb5GFViVCzeW%2BPI9qp8SRvtgin35brBb%2F%2FeSODvMgkQULA%3D%3D',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='58tongcheng')

    def final_parse(self, url):
        print(url)
        r = self.send_url(url)
        # try:
        #     r = requests.get(url=url, headers=self.headers, proxies=p)
        # except Exception as e:
        #     log.error(e)
        #     self.channel.basic_publish(exchange='',
        #                                routing_key='58tongcheng',
        #                                body=json.dumps(url))
        #     log.info('放队列 {}'.format(url))
        #     return
        tree = etree.HTML(r.text)
        try:
            city = tree.xpath('/html/body/div[2]/div[2]/a[3]/text()')[0].replace('小区', '')
        except:
            log.error('{}没有解析到城市'.format(url))
            return
        try:
            region = tree.xpath('/html/body/div[2]/div[2]/a[4]/text()')[0].replace('小区', '')
        except:
            log.error('{}没有解析到区域'.format(url))
            return
        try:
            name = tree.xpath('/html/body/div[2]/div[3]/span[1]/text()')[0]
        except:
            log.error('{}没有解析到名称'.format(url))
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
            'url':url
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

    @retry(delay=2, logger=log)
    def send_url(self, url):
        res = requests.get(url=url, headers=self.headers, proxies=p)
        return res


if __name__ == '__main__':
    for i in range(80):
        tongcheng = TongChengConsumer()
        threading.Thread(target=tongcheng.start_consuming).start()


