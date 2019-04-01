from multiprocessing import Process
from crawler.wenzhou_53 import Wenzhou
from crawler.xiamen_40 import Xiamen
from crawler.xinxiang_54 import Xinxiang
from crawler.xinyu_55 import Xinyu
from crawler.yantai_58 import Yantai
from crawler.yichang_63 import Yichang
from crawler.yichun_64 import Yichun
from crawler2.yueyang_66 import Yueyang
if __name__ == '__main__':
    a = Wenzhou()
    Process(target=a.start_crawler).start()
    b = Xiamen()
    Process(target=b.start_crawler).start()
    c = Xinxiang()
    Process(target=c.start_crawler).start()
    d = Xinyu()
    Process(target=d.start_crawler).start()
    e = Yantai()
    Process(target=e.start_crawler).start()
    f = Yichang()
    Process(target=f.start_crawler).start()
    g = Yichun()
    Process(target=g.start_crawler).start()
    h = Yueyang()
    Process(target=h.start_crawler).start()