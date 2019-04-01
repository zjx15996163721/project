import pika
import json

# 原来的队列,在 190服务器上
local_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='114.80.150.195',
    port=5673,
    heartbeat=0
))

local_channel = local_connection.channel()

# 将要放进去的队列
change_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='114.80.150.196',
    port=5673,
    heartbeat=0
))

change_channel = change_connection.channel()
change_channel.queue_declare(queue='amap_adb_street', durable=True)


def change_queue():
    local_channel.basic_qos(prefetch_count=1)
    local_channel.basic_consume(callback, queue='temporary_street')
    local_channel.start_consuming()


def callback(ch, method, properties, body):
    params = json.loads(body.decode())
    for param in params:
        new_queue(param)
    ch.basic_ack(delivery_tag=method.delivery_tag)


# 直接将要输入的关键字放入到队列中,一个一条消息
def new_queue(param):
    city_name = param['city_name']
    region = param['region']
    street = param['street']
    number = param['number']
    keyword = city_name + region + street + number + '号'
    print(keyword)
    change_channel.basic_publish(
        exchange='',
        routing_key='amap_adb_street',
        body=json.dumps(keyword),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )


if __name__ == '__main__':
    change_queue()
