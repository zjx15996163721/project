from postcode.get_city_region_consumer import Consumer
from postcode.get_city_region import GetCity, GetRegion
from multiprocessing import Process
from lib.proxy_iterator import Proxies
p = Proxies()
p = p.get_one(proxies_number=7)


if __name__ == '__main__':
    """
    获取城市，区域邮编
    """
    city = GetCity(p)
    city.get_province_city()
    """
    将城市，区域，道路邮编的URL放队列 
    """
    region = GetRegion(p)
    region.get_province_city_region()
    """
    消费队列中的URL
    """
    consumer = Consumer(p)
    for i in range(10):
        Process(target=consumer.start_consuming).start()