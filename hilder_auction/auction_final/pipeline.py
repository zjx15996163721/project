import pika
import yaml
from auction_final.exception import ConnectErrorException

setting = yaml.load(open('config.yaml'))


class Pipe(object):
    host = setting['rabbit']['host']
    port = setting['rabbit']['port']

    def __init__(self):
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, heartbeat=0))
        self.queue = 'auction'
        self.routing_key = 'auction'

    def produce(self, message):
        if message is None:
            raise ConnectErrorException('Message is empty!')
        elif isinstance(message, str):
            channel = self.__connection.channel()
            channel.queue_declare(queue=self.queue)
            channel.basic_publish(exchange='',
                                  routing_key=self.routing_key,
                                  body=message)
        else:
            raise ConnectErrorException('Message is not str!')

    def start_consume(self):
        channel = self.__connection.channel()
        channel.basic_qos(prefetch_count=20)
        channel.basic_consume(consumer_callback=self.callback, queue=self.queue)
        channel.start_consuming()

    def callback(self, ch, method, properties, body, ):
        """
        回调方法需要继承改写
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        msg = body.decode()
        print(msg)
        ch.basic_ack(delivery_tag=method.delivery_tag)
