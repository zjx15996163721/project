from crawler2.yangquan_62 import Yangquan
from crawler2.yangzhou_60 import Yangzhou
from crawler.suzhou_56 import Suzhou
from crawler.shenyang_45 import Shenyang
from crawler.taiyuan_49 import Taiyuan
from crawler.taian_50 import Taian
from crawler.tongling_51 import Tongling
from crawler.weihai_52 import Weihai

from multiprocessing import Process

if __name__ == '__main__':
    a = Yangquan()
    Process(target=a.start_crawler).start()
    b = Yangzhou()
    Process(target=b.start_crawler).start()

    c = Suzhou()
    Process(target=c.start_crawler).start()
    d = Shenyang()
    Process(target=d.start_crawler).start()
    e = Taiyuan()
    Process(target=e.start_crawler).start()
    f = Taian()
    Process(target=f.start_crawler).start()
    g = Tongling()
    Process(target=g.start_crawler).start()
    h = Weihai()
    Process(target=h.start_crawler).start()