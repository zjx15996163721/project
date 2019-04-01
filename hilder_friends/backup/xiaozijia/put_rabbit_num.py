from lib.rabbitmq import Rabbit
import yaml

setting = yaml.load(open('config.yaml'))

# rabbit
r = Rabbit(setting['xiaozijia']['rabbit']['host'], setting['xiaozijia']['rabbit']['port'])
channel = r.get_channel()
queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_num']
channel.queue_declare(queue=queue)


def put_rabbit():
    for i in range(1,350000):
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=str(i))


if __name__ == '__main__':
    put_rabbit()
