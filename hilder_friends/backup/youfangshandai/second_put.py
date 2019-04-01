import urllib3
import json
import pika
import certifi


class BuildingId:
    # 建立实例，声明管道，声明队列
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.190', port=5673))
    channel = connection.channel()
    channel.queue_declare(queue='yfsd_construction')

    # 设置代理IP
    # proxy = urllib3.ProxyManager('http://192.168.0.93:4234/', cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    }

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        # 获取队列中的数据
        if 'city' in body:
            city_url = body['city_url']
            con_id = body['con_id']
            city = body['city']
            # 发起第二次请求，得到楼房的Id
            response = self.http.request(
                'POST',
                city_url + '/wxp/yfsd/initHouseData',
                fields={'constructionId': str(con_id)},
                headers=self.headers,
            )
            if 'resultData' in response.data.decode():
                result = json.loads(response.data.decode())
                for j in result['resultData']:
                    buildingId = j['buildingId']
                    data = {
                        "buildingId": buildingId,
                        "city_url": city_url,
                        'city': city,
                    }
                    print(data)
                    self.channel.queue_declare(queue='yfsd_building')
                    self.channel.basic_publish(exchange='',
                                               routing_key='yfsd_building',
                                               body=json.dumps(data))
        else:
            print("-" * 30)
            print(body)
        # 告诉生产者，消息处理完成
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_start(self):
        # 类似权重，按能力分发
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                                   queue='yfsd_construction',
                                   )
        self.channel.start_consuming()


if __name__ == '__main__':
    b = BuildingId()
    b.consume_start()
