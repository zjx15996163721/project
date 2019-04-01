import pika
import requests
import json
import pymongo


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, ))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


url = 'http://www.fungugu.com/api/findChengShiLink'
headers = {
    'Cookie': 'jrbqiantai=F7CC7B6CB3323E1BDFECFFEEE4B829E1',
    'Referer': 'http://www.fungugu.com/JinRongGuZhi/toIndex',
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
}
proxies = {
    'http': 'http://192.168.0.98:4234/'
}
response = requests.post(url=url, headers=headers, proxies=proxies)
json_ = json.loads(response.text)
count = 0
channel = connect_rabbit('192.168.0.235', 'fgg_all_city_code')
comm_coll = connect_mongodb('192.168.0.136', 27017, 'fangjia', 'seaweed')
for i in json_['data']:
    data = i['data']
    for i in data:
        dict_ = {}
        city_name = i['MingCheng']
        count += 1
        print(city_name, count)

        if city_name in ['大连', '厦门']:
            for i in range(10000,23000):
                dict_['city_num'] = i
                dict_['city_name'] = city_name
                channel.basic_publish(exchange='',
                                      routing_key='fgg_all_city_code',
                                      body=json.dumps(dict_),
                                      )
        else:
            print(city_name)
