from wangyi.wangyi_producer import WangYi
from wangyi.wangyi_consumer import WangYiConsumer
from wangyi.insert_136 import insert_136
from multiprocessing import Process
# from lib.proxy_iterator import Proxies
# p = Proxies()
# p = p.get_one(proxies_number=1)

p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}

if __name__ == '__main__':
    # wangyiconsumer = WangYiConsumer(p)
    # wangyiconsumer.start_consuming()


    # wangyi_producer = WangYi(p)
    # wangyi_producer.start_crawler()

    insert_136()
