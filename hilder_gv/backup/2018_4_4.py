from multiprocessing import Process

from crawler.jiujiang_25 import Jiujiang
from crawler.kunming_26 import Kunming
from crawler.liupanshui_28 import Liupanshui
from crawler.loudi_29 import Loudi
from crawler.nanchang_31 import Nanchang
from crawler2.shanghai_42 import Shanghai
from crawler2.qingyuan_38 import Qingyuan
from crawler2.heyuan_17 import Heyuan
from crawler2.haikou_14 import Haikou
if __name__ == '__main__':

    a = Jiujiang()
    Process(target=a.start_crawler).start()
    b = Kunming()
    Process(target=b.start_crawler).start()
    c = Liupanshui
    Process(target=c.start_crawler).start()
    d = Loudi()
    Process(target=d.start_crawler).start()
    # e = Nanchang()
    # Process(target=e.start_crawler).start()
    f = Shanghai()
    Process(target=f.start_crawler).start()
    g = Qingyuan()
    Process(target=g.start_crawler).start()
    h = Heyuan()
    Process(target=h.start_crawler).start()
    i = Haikou()
    Process(target=i.start_crawler).start()