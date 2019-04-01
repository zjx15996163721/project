import pika
import hashlib
from retry import retry
import requests

credentials = pika.PlainCredentials('guest1', 'guest1')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '192.168.10.190', 5672, '/', credentials))

channel = connection.channel()
channel.queue_declare(queue='img_url_test')


class Download_image:
    @retry(tries=3)
    def request_(self, img, md5_url):
        response = requests.get(img)
        if response.status_code is 200:
            with open('image/{0}.png'.format(md5_url), 'wb') as f:
                f.write(response.content)
                print('1')
        else:
            print('错误url：', img)

    def callback(self, ch, method, properties, body):
        img = body.decode()
        m1 = hashlib.md5()
        m1.update(img.encode('utf-8'))
        md5_url = m1.hexdigest()
        try:
            self.request_(img, md5_url)
        except Exception as e:
            print(e)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_start(self):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback,
                              queue='img_url_test')
        channel.start_consuming()


if __name__ == '__main__':
    d = Download_image()
    d.consume_start()
