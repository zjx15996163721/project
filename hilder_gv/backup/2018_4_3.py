from crawler.dongwan_9 import Dongwan
from crawler.guiyang_13 import Guiyang

from crawler2.heyuan_17 import Heyuan
from crawler2.haikou_14 import Haikou


from crawler.fuzhou_11 import Fuzhou
from crawler.huizhou_21 import Huizhou
from crawler.jingmen_24 import Jingmen
from crawler.jieyang_23 import Jieyang
from crawler.huzhou_19 import Huzhou

from multiprocessing import Process
if __name__ == '__main__':
    a = Dongwan()
    Process(target=a.start_crawler).start()

    b = Guiyang()
    Process(target=b.start_crawler).start()

    c = Heyuan()
    Process(target=c.start_crawler).start()

    d = Haikou()
    Process(target=d.start_crawler).start()

    e = Fuzhou()
    Process(target=e.start_crawler).start()

    f = Huizhou()
    Process(target=f.start_crawler).start()

    g = Jingmen()
    Process(target=g.start_crawler).start()

    h = Jieyang()
    Process(target=h.start_crawler).start()

    i = Huzhou()
    Process(target=i.start_crawler).start()