from crawler.centaline import Centaline
from crawler.fangtu import Fangtu
from crawler.kufangwang import Kufangwang
from crawler.leju import Leju
from crawler.maitian import Maitian
from crawler.qfangwang import Qfangwang
from crawler.taiwuwang import Taiwuwang
from crawler.woai import Woai
from crawler.fangtianxia import Fangtianxia
from multiprocessing import Process
from crawler.lianjia_producer import LianjiaProducer
from lib.proxy_iterator import Proxies
from crawler.fangtianxia_consumer import FangtianxiaConsumer
from crawler.lianjiazaixian_consumer import LianJiaConsumer
import threading
p = Proxies()
p = p.get_one(proxies_number=7)
# p = {'http': 'http://lum-customer-fangjia-zone-static:ezjbr7lcghy0@zproxy.lum-superproxy.io:22225'}


if __name__ == '__main__':
    # centaline = Centaline(p)
    # fangtianxia = Fangtianxia(p)
    # fangtu = Fangtu(p)
    # kufangwang = Kufangwang(p)
    # leju = Leju(p)
    # lianjia = LianjiaProducer(p)
    # maitian = Maitian(p)
    # qfangwang = Qfangwang(p, 'qchatid=80fb425b-d9ad-407a-b329-5f5ac4b3ffb5; cookieId=91223fe9-4cbb-4081-a714-4a6134d34384; JSESSIONID=aaaRMNiXdRWXGcIX1-Eyw; WINDOW_DEVICE_PIXEL_RATIO=1; CITY_NAME=DONGGUAN; _ga=GA1.3.2005953466.1538118346; _qzjc=1; _jzqa=1.4319550797732626000.1538285023.1538285023.1538285023.1; _jzqc=1; _jzqx=1.1538285023.1538285023.1.jzqsr=dongguan%2Eqfang%2Ecom|jzqct=/.-; SALEROOMREADRECORDCOOKIE=100337096; looks=SALE%2C100337096%2C1107059; _qzja=1.1899643087.1538285022820.1538285022820.1538285022821.1538285022821.1538285038735.0.0.0.2.1; sid=24578a94-4a56-4216-b3da-1f4642589c57; _gid=GA1.3.1191001263.1541487501; Hm_lvt_de678bd934b065f76f05705d4e7b662c=1541487501; fuid=dac2cc94-dde7-46f8-b26c-35d2a4503ce0; userId=9007231; userName=Q%E6%88%BF%E7%94%A8%E6%88%B7; accountId=8baf6181-7955-4020-bb63-a906340e00f8; loginphone=15996163721; city=SHANGHAI; Hm_lpvt_de678bd934b065f76f05705d4e7b662c=1541488914')
    # taiwuwang = Taiwuwang(p)
    # woai = Woai(p)
    # Process(target=centaline.start_crawler).start()
    # Process(target=fangtianxia.start_crawler).start()
    # Process(target=fangtu.start_crawler).start()
    # Process(target=kufangwang.start_crawler).start()
    # Process(target=leju.start_crawler).start()
    # Process(target=lianjia.start_crawler).start()
    # Process(target=maitian.start_crawler).start()
    # Process(target=qfangwang.start_crawler).start()
    # Process(target=taiwuwang.start_crawler).start()
    # Process(target=woai.start_crawler).start()

    # 房天下
    # for i in range(50):
    #     fang = FangtianxiaConsumer(p)
    #     threading.Thread(target=fang.start_consuming).start()

    # 链家在线
    for i in range(50):
        lianjia = LianJiaConsumer(p)
        threading.Thread(target=lianjia.start_consuming).start()




