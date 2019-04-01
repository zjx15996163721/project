from ceic.detail import Detail
from ceic.ceic_crawler import CEIC
from multiprocessing import Process
import schedule
from ceic.split_url import ProducerUrl, ConsumerUrl

if __name__ == '__main__':
    # # 开启 ceic 首页
    # c = CEIC()
    # c.crawler()

    # 开启ceic详情
    # d = Detail()
    #
    # d.get_url()
    # Process(target=d.get_url).start()
    # for i in range(10):
    #     Process(target=d.get_url).start()

    # p = ProducerUrl()
    # p.put_url_in_queue()

    c = ConsumerUrl()

    # for i in range(10):
    #     Process(target=c.start_consumer).start()
    c.start_consumer()
