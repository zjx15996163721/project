"""
爬取顺序：城市-区域-街道-菜系
start:8
"""
from lib.rabbitmq import Rabbit
import re, json, datetime, requests
from lib.mongo import Mongo
import random
import yaml
import uuid
from dianping.rk import RClient
from lib.log import LogHandler
from fake_useragent import UserAgent

ua = UserAgent()

setting = yaml.load(open('config.yaml'))

log = LogHandler('dianping')

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
coll_update = m.connect['crawler_dianping']['shop_info_new']

rc = RClient('ruokuaimiyao', '205290mima', '95632', '6b8205cf61944329a5841c30e5ed0d5d')

headers = {
    'User-Agent': ua.random,
    'Cookie': '_hc.v="\"b3d876d6-0e1d-49bf-a9b5-01b4a2d93a86.1528188183\""; cy=1; cye=shanghai; _lxsdk_cuid=163cf1d1d63c8-030c43b96ca8-39614101-1aeaa0-163cf1d1d63c8; _lxsdk=163cf1d1d63c8-030c43b96ca8-39614101-1aeaa0-163cf1d1d63c8; s_ViewType=10; _lxsdk_s=163cf1d1d65-63d-4f0-7a3%7C%7C104',
}


def request_get(url, ip):
    try:
        proxies = {
            'http': ip,
            'https': ip,
        }
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
        connection.process_data_events()
        if 'name="Description"' in response.text:
            print(ip, '¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿')
            return response
        elif '错误信息：请求错误' in response.text:
            print('url无效，url={}'.format(url))
            return 'un_url'
        elif '验证中心' in response.text:
            response = login_dianping(response.text, ip, url)
            if response:
                print('验证成功')
                return response
            else:
                return None
        else:
            return None

    except Exception as e:

        print(e)
        return None


def login_dianping(html, ip, url):
    requestCode = re.search('requestCode: "(.*?)"', html, re.S | re.M).group(1)
    _token = str(random.randint(1, 100000))
    randomId = str(random.random())
    action = 'spiderindefence'
    url_img = 'https://verify.meituan.com/v2/captcha?' + 'request_code=' + requestCode + '&action=' + action + '&randomId=' + randomId + '&_token' + _token
    proxy = {
        'http': ip,
        'https': ip
    }
    while True:
        print('开始验证', ip)
        res = requests.get(url_img, proxies=proxy, timeout=20)
        connection.process_data_events()
        html_img = res.content
        img_result_res = rc.rk_create(html_img, 3040)
        if 'Result' not in img_result_res:
            print('快豆不足')
            continue
        img_result = img_result_res['Result']
        rk_id = img_result_res['Id']
        uuid_name = str(uuid.uuid1())
        if html_img:
            with open('./images/%s_%s.jpg' % (img_result, uuid_name), 'wb') as f:
                f.write(html_img)
        data = {
            'id': '71',
            'request_code': requestCode,
            'captchacode': img_result,
            '_token': _token
        }
        v_url = 'https://verify.meituan.com/v2/ext_api/spiderindefence/verify?id=1'
        response = requests.post(v_url, data=data, headers=headers, proxies=proxy, timeout=30)
        connection.process_data_events()
        if '请求异常,拒绝操作' in response.text:
            v_url = 'https://verify.meituan.com/v2/ext_api/spiderindefence/verify?id=1'
            response = requests.post(v_url, data=data, headers=headers, proxies=proxy, timeout=30)
            connection.process_data_events()
            if '请求异常,拒绝操作' in response.text:
                return None
        if 'response_code' not in response.text:
            continue
        response_code = response.json()['data']['response_code']
        end_url = 'https://optimus-mtsi.meituan.com/optimus/verifyResult?originUrl=' + url + '&response_code=' + response_code + '&request_code=' + requestCode
        end_res = requests.get(end_url, headers=headers, proxies=proxy, timeout=20)
        connection.process_data_events()
        if 'name="Description"' in end_res.text:
            with open('./images_right/%s_%s.jpg' % (img_result, uuid_name), 'wb') as f:
                f.write(html_img)
            return end_res
        elif '大众点评网' in end_res.text:
            return None
        else:
            pass


def callback(ch, method, properties, body):
    ip = method.consumer_tag
    body = json.loads(body.decode())
    city = body['city'][0]
    url = body['url']
    shop_id = body['shop_id']
    is_exist = coll_update.find_one({'shop_id': shop_id})
    if is_exist:
        log.info('商店id已经存在，shop_id="{}"'.format(shop_id))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    connection.process_data_events()
    response = request_get(url, ip)
    try:
        if response == 'un_url':
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        html = response.text
        area_html = re.search('<div class="breadcrumb">.*?</div>', html, re.S | re.M).group()
        area_list = re.findall('<a.*?>(.*?)<', area_html, re.S | re.M)[1:]
        shop_name = re.search('<span>(.*?)</span>', area_html, re.S | re.M).group(1)
        try:
            food_kind = area_list[0]
            area = ("、").join(area_list[1:])
        except Exception as e:
            food_kind = None
            area = None
        try:
            comment_html = re.search('id="comment_score".*?</div>', html, re.S | re.M).group()
            comment_list = re.findall('<span.*?>(.*?)<', comment_html, re.S | re.M)
            comment = (' ').join(comment_list)
        except Exception as e:
            comment = None
        rank_stars = re.search('brief-info.*?title="(.*?)"', html, re.S | re.M).group(1)
        address = re.search('地址：.*?title="(.*?)"', html, re.S | re.M).group(1)
        try:
            mean_price = re.search('avgPriceTitle.*?人均:(.*?)<', html, re.S | re.M).group(1)
        except Exception as e:
            mean_price = None
        x = re.search('shopGlat.*?"(.*?)"', html, re.S | re.M).group(1)
        y = re.search('shopGlng.*?"(.*?)"', html, re.S | re.M).group(1)
        data = {
            'lat_x': x,
            'long_y': y,
            'city': city,
            'shop_name': shop_name,
            'food_kind': food_kind,
            'area': area,
            'comment': comment,
            'rank_stars': rank_stars,
            'address': address,
            'mean_price': mean_price,
            'shop_id': shop_id,
            'update_time': datetime.datetime.now()
        }
        print(data)
        coll_update.insert_one(data)
        html_data = {'html': html, 'shop_name': shop_name, 'url': url, 'shop_id': shop_id}
        coll_html.insert_one(html_data)

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
    ips = [
        "192.168.0.90:4234",
        "192.168.0.93:4234",
        "192.168.0.94:4234",
        "192.168.0.96:4234",
        "192.168.0.98:4234",
        "192.168.0.99:4234",
        "192.168.0.100:4234",
        "192.168.0.101:4234",
        "192.168.0.102:4234",
        # "192.168.0.103:4234",
        # '118.114.77.47:8080'
    ]
    from multiprocessing import Process

    for i in ips:
        Process(target=consume_start, args=(i,)).start()

    # consume_start("192.168.0.100:4234")
