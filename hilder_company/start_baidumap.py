# _*_ coding:utf-8 _*_
# from company.baidumap_consumer import BaiduMapConsumer
from company.baidumap_producer import baiduproducer

from lib.proxy_iterator import Proxies
from multiprocessing import Process
from company.baidumap_consumer_update import BaiduMapConsumer

if __name__ == '__main__':
    # Process(target=baiduproducer).start()

    p = Proxies()
    # # Process(target=BaiduMapConsumer(proxies=next(p)).start_consume).start()
    #
    for x in range(1,7):
        Process(target=BaiduMapConsumer(proxies=p.get_one(x)).start_consume).start()

    # proxy = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    #     "host": "http-dyn.abuyun.com",
    #     "port": "9020",
    #     "user": "HPULN86JD485HB3D",
    #     "pass": "673E8811D7D77884",
    # }
    # proxies = {"https": proxy,
    #            "http": proxy}
    # Process(target=BaiduMapConsumer(proxies=proxies).start_consume).start()
