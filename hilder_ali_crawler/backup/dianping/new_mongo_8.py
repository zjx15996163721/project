from lib.rabbitmq import Rabbit
import json
import yaml
import re
import datetime
from lib.log import LogHandler
from dianping.request_detail import request_get
from lxml import etree
from lib.mongo import Mongo

setting = yaml.load(open('config.yaml'))
log = LogHandler('dianping_detail')

# rabbit
r = Rabbit(setting['dianping']['rabbit']['host'], setting['dianping']['rabbit']['port'])
connection = r.connection

channel = connection.channel()
all_url_queue = setting['dianping']['rabbit']['queue']['all_url_queue']
channel.queue_declare(queue=all_url_queue)

# mongo
m = Mongo(setting['dianping']['mongo']['host'], setting['dianping']['mongo']['port'])
coll = m.connect[setting['dianping']['mongo']['db']][setting['dianping']['mongo']['save_coll']]
coll_html = m.connect[setting['dianping']['mongo']['db']]['html']
coll_update = m.connect['crawler_dianping']['shop_info_all_type']

kind_list = {
    'ch10': '美食',
    'ch30': '休闲娱乐',
    'ch50': '丽人',
    'ch35': '周边游',
    'ch45': '运动健身',
    'ch20': '购物',
    'ch75': '学习培训',
    'ch80': '生活服务',
    'ch85': '医疗健康',
    'ch65': '爱车',
    'ch95': '宠物',
    'ch90': '家装',
    'ch70': '亲子',
    'hotel/': '酒店',
    'ch55': '结婚',
}


def anlayzer_mongo(html, shop_id, city, kind_code, info):
    tree = etree.HTML(html)
    try:
        if kind_code == 'ch75' or kind_code == 'ch30':
            area_info_str = tree.xpath('//*[@class="inner"]/a/text()')
            shop_name = tree.xpath('//div[@class="shop-name"]/h1/text()')[0]
            address = tree.xpath('//div[@class="address"]/text()')[1].strip()
            rank_stars_str = tree.xpath('//div[@class="rank"]/span[1]//@class')[0]
            rank_stars = str(int(re.search('str(\d+)', rank_stars_str).group(1)) / 10)
            comment_list = tree.xpath('//div[@class="rank"]/span[@class="item"]/text()')
            mean_price = None
            x = re.search('lat:(.*?)\}', html, re.S | re.M).group(1)
            y = re.search('lng:(.*?),', html, re.S | re.M).group(1)
        else:
            area_info_str = tree.xpath('//*[@id="body"]/div/div[1]/a/text()')
            shop_name = tree.xpath('//h1[@class="shop-name"]/text()')[0]
            mean_price = tree.xpath('//*[@id="avgPriceTitle"]/text()')[0]
            address = re.search('address: "(.*?)",', html, re.S | re.M).group(1)
            rank_stars = tree.xpath('//div[@class="brief-info"]//@title')[0]
            comment_list = tree.xpath('//span[@id="comment_score"]/span/text()')
            x = re.search('shopGlat.*?"(.*?)"', html, re.S | re.M).group(1)
            y = re.search('shopGlng.*?"(.*?)"', html, re.S | re.M).group(1)
        area_info = ('/').join(area_info_str)
        comment = (' ').join(comment_list)
        data = {
            'lat_x': x,
            'long_y': y,
            'city': city,
            'shop_name': shop_name,
            'area_info': area_info,
            'comment': comment,
            'rank_stars': rank_stars,
            'address': address,
            'mean_price': mean_price,
            'shop_id': shop_id,
            'update_time': datetime.datetime.now(),
            'kind_code': kind_list[kind_code],
            'info': info
        }
        print(data)
        coll.insert_one(data)
        return data
    except Exception as e:
        log.info('类型与给定类型不一样，city="{}",shop_id="{}",e="{}"'.format(city, shop_id, e))
        return False


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    city = body['city'][0]
    url = body['url']
    shop_id = body['shop_id']
    kind_code = body['kind_code']
    info = body['info']
    response = request_get(url, ip, connection)
    try:
        if response == 'un_url':
            log.info('此url没有商店，url={}'.format(url))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        html = response.text
        # 查询原网页保存了没
        is_exist = coll_html.find_one({'url': url})
        if not is_exist:
            data_html = {
                'html': html,
                'url': url,
            }
            coll_html.insert_one(data_html)
        data = anlayzer_mongo(html, shop_id, city, kind_code, info)
        if data:
            coll_update.update_one({'shop_id': shop_id}, {'$set': data})
    except Exception as e:
        connection.process_data_events()
        channel.basic_publish(exchange='',
                              routing_key=all_url_queue,
                              body=json.dumps(body),
                              )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_start(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=all_url_queue, consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-dyn.abuyun.com", "port": "9020",
                                                         "user": "H51910O3VL7534QD", "pass": "42DE00B25FC5330C"}
    consume_start(ip)
