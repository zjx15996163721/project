from crawler2.guigang_150 import Guigang
from crawler2.nanning_88 import Nanning
from crawler2.nanjing_74 import Nanjing
from crawler2.anshun_149 import Anshun
from crawler2.wuhan_78 import Wuhan
from crawler.nantong_89 import Nantong
from crawler.weifang_95 import Weifang
from crawler.cangzhou_103 import Cangzhou
from crawler.anyang_99 import Anyang
from crawler.yanji_147 import Yanji
from crawler.longyan_138 import Longyan
from multiprocessing import Process

if __name__ == '__main__':
    a = Guigang()
    b = Nanning()
    c = Nanjing()
    d = Anshun()
    e = Wuhan()
    f = Nantong()
    g = Weifang()
    h = Cangzhou()
    i = Anyang()
    j = Yanji()
    k = Longyan()
    Process(target=a.start_crawler).start()
    Process(target=b.start_crawler).start()
    Process(target=c.start_crawler).start()
    Process(target=d.start_crawler).start()
    Process(target=e.start_crawler).start()
    Process(target=f.start_crawler).start()
    Process(target=g.start_crawler).start()
    Process(target=h.start_crawler).start()
    Process(target=i.start_crawler).start()
    Process(target=j.start_crawler).start()
    Process(target=k.start_crawler).start()



