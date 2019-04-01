from lib.rabbitmq import Rabbit

r = Rabbit('127.0.0.1', 5673)
channel = r.get_channel()

for i in range(50000):
    print(i)
    channel.queue_declare(queue='fgg_number')
    channel.basic_publish(exchange='',
                          routing_key='fgg_number',
                          body=str(i))
