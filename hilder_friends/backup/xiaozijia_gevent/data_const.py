from lib.rabbitmq import Rabbit
import json

r = Rabbit('localhost', 5673)
channel = r.get_channel()
list_ = []


def data_const(ch, method, properties, body):
    global list_
    data = json.loads(body.decode())
    ConstructionName = data['ConstructionName']
    Id = data['Id']
    channel.queue_declare(queue='xiaozijia_house_detail')
    channel.basic_publish(exchange='',
                          routing_key='xiaozijia_house_detail',
                          body=body)
    save_data = {"Id": Id, "ConstructionName": ConstructionName}
    list_.append(json.dumps(save_data))
    if len(list_) % 50 == 0:
        channel.queue_declare(queue='xiaozijia_gevent')
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_gevent',
                              body=json.dumps(list_))
        print(list_)
        list_ = []
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=data_const, queue='xiaozijia_house_detail')
    channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
