from xiaozijia_gevent.consumer_xiaozijia_gevent import consume_queue

if __name__ == '__main__':
    for i in range(20):
        consume_queue()
