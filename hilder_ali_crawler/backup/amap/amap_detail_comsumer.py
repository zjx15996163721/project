from lib.rabbitmq import Rabbit
import trip
from functools import partial
import json
from lib.mongo import Mongo
from lib.log import LogHandler

log = LogHandler('amap')

m = Mongo('192.168.0.235', 27017)
coll_save = m.connect['amap']['2018-5-9-detail_test']


def requests_a(result):
    url = result.url
    print(result.json())
    response = result.json()
    if response['status'] == "1":
        if response['count'] == '1':
            coll_save.insert_one(response)
        else:
            log.debug('amap ,count 不为1，url={}'.format(url))

    else:
        log.debug('amap ,status 不为1，url={}'.format(url))


@trip.coroutine
def asyn_message(body):
    r = yield [trip.get(url) for url in json.loads(body.decode())]
    for result in r:
        requests_a(result)


def callback(ch, method, properties, body):
    trip.run(partial(asyn_message, body))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_all_url():
    rabbit = Rabbit(host='192.168.0.192', port=5673)
    connect_result = rabbit.connection
    channel = connect_result.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='amap_test')
    channel.start_consuming()


if __name__ == '__main__':
    consume_all_url()
    # from multiprocessing import Process
    # for i in range(15):
    #     Process(target=consume_all_url).start()
    #