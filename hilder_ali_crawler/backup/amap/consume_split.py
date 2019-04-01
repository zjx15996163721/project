"""
这个也没用 2018/4/12 别看了
切割经纬度
"""
import json
import re
import pika
import requests
import sys

sys.setrecursionlimit(1000000)
api_key = ['291073f17ee0b963ccb1927ed92bf265', ]
count_ = 0


def get_poi(start_lon_get, start_sat_get, end_lon_get, end_sat_get, type_):
    print(start_lon_get, start_sat_get, end_lon_get, end_sat_get, )
    global count_
    count_ += 1
    # print(count_)
    print('递归')
    square_ = str(start_lon_get) + ',' + str(start_sat_get) + ';' + str(end_lon_get) + ',' + str(end_sat_get)
    url = 'http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + type_ + '&output=JSON&key=' + \
          api_key[0] + '&offset=50'
    print(url)
    response = requests.get(url)
    result_count = response.json().get('count')
    print(result_count)
    if response.json().get('status') is '1':
        if int(result_count) > 850:
            a, b, c, d = split_rectangle(start_lon_get, start_sat_get, end_lon_get, end_sat_get, )
            get_poi(a[0], a[1], a[2], a[3], type_)
            get_poi(b[0], b[1], b[2], b[3], type_)
            get_poi(c[0], c[1], c[2], c[3], type_)
            get_poi(d[0], d[1], d[2], d[3], type_)
        else:
            if int(result_count) != 0:
                if int(result_count) < 50:
                    rabbit.queue_declare(queue='amap_result_json')
                    rabbit.basic_publish(exchange='', routing_key='amap_result_json', body=json.dumps(response.json()))
                else:
                    rabbit.queue_declare(queue='amap_page_url')
                    for i in range(1, int(int(result_count) / 50 + 0.5)):
                        rabbit.basic_publish(exchange='',
                                             routing_key='amap_page_url',
                                             body='http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + type_ + '&output=JSON&offset=50&page=' + str(
                                                 i + 1),
                                             )
                        print('分页url放入')
            else:
                print('count:', result_count)
    else:
        print('result status', response.json().get('status'))


def split_rectangle(start_lon_, start_sat_, end_lon_, end_sat_, ):
    """
    给两个点算中点，返回4组数据
    right_up_sq-> left_up_sq-> right_down_sq-> left_down_sq
    :param start_lon_:
    :param start_sat_:
    :param end_lon_:
    :param end_sat_:
    :return:
    """

    m = (start_lon_ - end_lon_) / 2  # 横向距离/2
    s = (start_sat_ - end_sat_) / 2  # 纵向距离/2

    middle_lon = start_lon_ - m
    middle_sat = start_sat_ - s

    right_up_sq = [start_lon_, start_sat_, middle_lon, middle_sat, ]

    left_up_sq = [middle_lon, start_sat_, end_lon_, middle_sat]

    right_down_sq = [start_lon_, middle_sat, middle_lon, end_sat_]

    left_down_sq = [middle_lon, middle_sat, end_lon_, end_sat_]

    print(right_up_sq, left_up_sq, right_down_sq, left_down_sq)
    return right_up_sq, left_up_sq, right_down_sq, left_down_sq


def callback(ch, method, properties, body):
    body = json.loads(body.decode('utf8'))
    square_ = body['square_list']
    type_ = body['type']
    num_list = re.split(r',|;', square_)
    start_lon_ = float(num_list[0])
    start_sat_ = float(num_list[1])
    end_lon_ = float(num_list[2])
    end_sat_ = float(num_list[3])
    print(start_lon_, start_sat_, end_lon_, end_sat_, )
    a, b, c, d = split_rectangle(start_lon_, start_sat_, end_lon_, end_sat_, )
    get_poi(a[0], a[1], a[2], a[3], type_)
    get_poi(b[0], b[1], b[2], b[3], type_)
    get_poi(c[0], c[1], c[2], c[3], type_)
    get_poi(d[0], d[1], d[2], d[3], type_)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_split(channel):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='amap_split',
                          )
    channel.start_consuming()


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.235', ))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_split')
    consume_split(rabbit)
