from ceic.consumer_detail import Consumer
from multiprocessing import Process

if __name__ == '__main__':
    ips = ["192.168.0.96:4234",
           "192.168.0.93:4234",
           "192.168.0.90:4234",
           "192.168.0.94:4234",
           "192.168.0.98:4234",
           "192.168.0.99:4234",
           "192.168.0.100:4234",
           "192.168.0.101:4234",
           "192.168.0.102:4234",
           "192.168.0.103:4234", ]
    c = Consumer()
    # c.consume_start("192.168.0.96:4234")
    for i in ips:
        Process(target=c.consume_start, args=(i,)).start()
