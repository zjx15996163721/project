from company.lagou_force import LagouProducer
from company.lagou_force import LagouConsumer
from lib.proxy_iterator import Proxies
from multiprocessing import Process

if __name__ == '__main__':
    # 1.放入队列操作
    Process(target=LagouProducer().put_url_into_queue()).start()


    #2.开始消费操作
    p = Proxies()
    for i in range(6):
        l = LagouConsumer(next(p))
        Process(target=l.start_consumer).start()
