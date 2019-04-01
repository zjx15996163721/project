from dianping.category_orm import City, get_sqlalchemy_session, Region, SecondCategory
from lib.proxy_iterator import Proxies
from multiprocessing import Process
from dianping.producer import Controller
from dianping.consumer import Consumer
from dianping.get_all_city import GetRegion, GetAllCity
from dianping.convert_id_rpc_server import ConvertIdRpcServer
p = Proxies()

db_session = get_sqlalchemy_session()

if __name__ == '__main__':
    """
    获取城市
    """
    # city = GetAllCity()
    # city.get_all_city()
    """
    获取区域和二级分类,更新count
    """
    for city in db_session.query(City):
        g = GetRegion(city)
        g.get_region()

    """
    把所有城市放入队列
    """
    c = Controller(next(p))
    for i in db_session.query(City):
        c.crawler_by_city(i)
        print('开始抓取城市={}'.format(i.name))

    """
    消费所有城市
    """
    for i in range(6):
        c = Consumer(next(p))
        Process(target=c.start_consume).start()

    """
    RPC调用,恢复没有ID的数据
    """
    convert_id = ConvertIdRpcServer(next(p))
    convert_id.start_consuming()

