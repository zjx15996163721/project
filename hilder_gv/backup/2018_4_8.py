from multiprocessing import Process
from crawler.nanchang_31 import Nanchang
from crawler.liupanshui_28 import Liupanshui

from crawler.ningbo_33 import Ningbo
from crawler.nanping_32 import Nanping
from crawler.ningde_34 import Ningde
from crawler.pingdingshan_36 import Pingdingshan
from crawler.qingdao_37 import Qingdao
from crawler.ninghai_35 import Ninghai
from crawler.shantou_41 import Shantou

if __name__ == '__main__':
    a = Nanchang()
    Process(target=a.start_crawler).start()
    b = Liupanshui()
    Process(target=b.start_crawler).start()

    c = Ningbo()
    Process(target=c.start_crawler).start()
    d = Nanping()
    Process(target=d.start_crawler).start()
    e = Ningde()
    Process(target=e.start_crawler).start()
    f = Pingdingshan()
    Process(target=f.start_crawler).start()
    g = Qingdao()
    Process(target=g.start_crawler).start()
    # h = Ninghai()
    # Process(target=h.start_crawler).start()
    i = Shantou()
    Process(target=i.start_crawler).start()