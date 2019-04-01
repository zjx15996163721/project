"""
这个文件的分的方法拿不到全部的poi，放弃不用了
"""
import pika
import json

# 祖传切割（不使用）
# def request_amap(square_, type_):
#     """
#     apmap_result_json：pois
#     amap_page_url：分页url
#     amap_split: 等待切分
#     :param square_:
#     :param type_:
#     :return:
#     """
#     square_ = str(square_[0]) + ',' + str(square_[1]) + ';' + str(square_[2]) + ',' + str(square_[3])
#     print(square_)
#     url = 'http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + type_ + '&output=JSON&key=' + \
#           api_key[0] + '&offset=50'
#     result = requests.get(url, )
#     status = result.json()['status']
#     if status is '1':
#         count = int(result.json()['count'])
#         if count > 800:
#             body = json.dumps({'square_list': square_, 'type': type_})
#             rabbit.basic_publish(exchange='', routing_key='amap_split', body=body)
#         else:
#             if count != 0:
#                 if count < 50:
#                     print('count < 50')
#                     rabbit.queue_declare(queue='amap_result_json')
#                     rabbit.basic_publish(exchange='', routing_key='amap_result_json', body=json.dumps(result.json()))
#                     print(result.json())
#
#                 else:
#                     rabbit.queue_declare(queue='amap_page_url')
#                     for i in range(1, int(count / 50 + 0.5)):
#                         rabbit.basic_publish(exchange='',
#                                              routing_key='amap_page_url',
#                                              body='http://restapi.amap.com/v3/place/polygon?polygon=' + square_ + ';&types=' + type_ + '&output=JSON&offset=50' + '&page=' + str(
#                                                  i + 1),
#                                              )
#                         print('分页 的url放入')
#             else:
#                 print('count = 0')


def all_url(a_type, rabbit):
    """
    获取所有的行
    :param a_type:
    :return:
    """
    start_lon = 72.510906
    start_sat = 53.971043

    end_lon = start_lon + 0.5
    end_sat = start_sat - 0.5

    for i in range(1000):
        if start_lon < 135.135304:
            start_lon = start_lon + 0.5
            start_sat = start_sat

            end_lon = end_lon + 0.5
            end_sat = end_sat
            square_list = [start_lon, start_sat, end_lon, end_sat]
            body = json.dumps({'square_list': square_list, 'type': a_type})
            rabbit.basic_publish(exchange='',
                                 routing_key='amap_all_url',
                                 body=body,
                                 properties=pika.BasicProperties(
                                     delivery_mode=2,  # make message persistent
                                 )
                                 )
            get_y(start_lon, start_sat, end_lon, end_sat, a_type, rabbit)


def get_y(start_lon, start_sat, end_lon, end_sat, a_type, rabbit):
    """
    获取所有的列
    :param start_lon:
    :param start_sat:
    :param end_lon:
    :param end_sat:
    :param a_type:
    :return:
    """
    for j in range(1000):
        if start_sat > 19.349285:
            start_lon = start_lon
            start_sat = start_sat - 0.5

            end_lon = end_lon
            end_sat = end_sat - 0.5
            square_list = [start_lon, start_sat, end_lon, end_sat]
            body = json.dumps({'square_list': square_list, 'type': a_type})
            rabbit.basic_publish(exchange='',
                                 routing_key='amap_all_url',
                                 body=body,
                                 properties=pika.BasicProperties(
                                     delivery_mode=2,  # make message persistent
                                 )
                                 )


def put_all_url_into_queue():
    type_list = ['010000', '020000', '030000', '040000', '050000', '060000', '070000', '080000', '090000',
                 '100000', '110000', '120000', '130000', '140000', '150000', '160000', '170000', '180000',
                 '190000', '200000', '220000', ]
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.235', ))
    rabbit = connection.channel()
    rabbit.queue_declare(queue='amap_all_url')
    for a_type in type_list:
        all_url(a_type, rabbit)


if __name__ == '__main__':
    put_all_url_into_queue()
