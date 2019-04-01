import pika
from retry import retry
import time


class Rabbit:
    def __init__(self, host, port):
        self.connection = self.connect_rabbit(host, port)

    @staticmethod
    @retry(tries=-1)
    def connect_rabbit(host, port):
        try:
            print('建立pika连接')
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, heartbeat_interval=0))
            return connection
        except Exception as e:
            print('重新连接pika')
            time.sleep(5)
            raise

    def get_connection(self):
        return self.connection

    def get_channel(self):
        return self.connection.channel()


if __name__ == '__main__':
    for i in range(5670, 5674):
        r = Rabbit('192.168.0.190', i)
        channel = r.get_channel()
        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body='Hello World!')
        print(" [x] Sent 'Hello World!'")
