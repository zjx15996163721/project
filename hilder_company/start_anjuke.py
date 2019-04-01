from gevent import monkey
monkey.patch_all()
# from match.anjuke_producer_city import analyse_city
# from match.anjuke_producer_detai_url import AnjukeProducer
# from lib.proxy_iterator import Proxies
# from multiprocessing import Process
from match.anjuke_consumer import AnjukeNewConsumer,AnjukeLoupanConsumer

if __name__ == '__main__':
    proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
        "host": "http-proxy-sg2.dobel.cn",
        "port": "9180",
        "account": "FANGJIAHTT7",
        "password": "HGhyd7BF",
    }
    proxies = {"https": proxy,
               "http": proxy}


    #1.将安居客上所有的城市安居客的主页链接放入到队列中
    # Process(target=analyse_city,args=(proxies,)).start()

    # #2.将安居客写字楼详情页链接放入到队x列中
    # for x in range(1,7):
    #     Process(target=AnjukeProducer(proxies=p.get_one(proxies_number=x)).start_consume).start()
    # Process(target=AnjukeProducer(proxies=proxies).start_consume).start()
    # #
    # # # #3.消费2中写字楼信息,三个进程,分别消费出租\出售\新盘三种类型
    # # # # Process(target=AnjukeNewConsumer(proxies=next(p)).start_consume).start()
    # # # Process(target=AnjukeLoupanConsumer(proxies=p.get_one(proxies_number=2)).start_consume).start()
    # #
    # Process(target=AnjukeNewConsumer(proxies=proxies).start_consume).start()
    # Process(target=AnjukeLoupanConsumer(proxies=proxies).start_consume).start()

    lou = AnjukeLoupanConsumer(proxies)
    lou.start_consume()

    # new = AnjukeNewConsumer(proxies)
    # new.start_consume()


    # for x in range(1,4):
    #     Process(target=AnjukeLoupanConsumer(proxies=p.get_one(proxies_number=x)).start_consume).start()
    # for x in range(4,7):
    #     Process(target=AnjukeNewConsumer(proxies=p.get_one(proxies_number=x)).start_consume).start()
    # Process(target=AnjukeLoupanConsumer(proxies=proxies).start_consume).start()
    # Process(target=AnjukeNewConsumer(proxies=proxies).start_consume).start()
    # Process(target=AnjukeNewConsumer(proxies=next(p)).start_consume).start()