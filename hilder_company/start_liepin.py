"""
猎聘运行是3，4
"""
# from company.liepin_category import get_city,get_category
from company.liepin_producer_list import LiepinProduceList
from lib.proxy_iterator import Proxies
from multiprocessing import Process
from company.liepin_consumer_single import LiepinConsumeSingle
from company.liepin_producer_detail import LiepinProducerDetail
from company.liepin_consumer_gevent import LiepinConsumeGevent
if __name__ == '__main__':
    #1.分别将城市代码及分类代码存入到mysql数据库中
    # get_city()
    # get_category()

    #2.生产者,将分页也就是列表页链接放入到队列中
    p = Proxies()
    Process(target=LiepinProduceList(proxies=next(p)).start_crawler).start()

    #3.生产者,消费2中队列的url,解析出来公司的url,将公司详情页放入到队列中
    Process(target=LiepinProducerDetail(proxies=next(p)).start_consume).start()

    #4.消费3中队列中的URL,发请求\解析\入库
    p = Proxies()
    for x in range(1,7):
        Process(target=LiepinConsumeSingle(proxies=p.get_one(proxies_number=x)).start_consume).start()

    proxy = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": "http-dyn.abuyun.com",
        "port": "9020",
        "user": "HPULN86JD485HB3D",
        "pass": "673E8811D7D77884",
    }
    proxies = {"https": proxy,
               "http": proxy}
    Process(target=LiepinConsumeGevent(proxies=proxies).start_consume).start()











