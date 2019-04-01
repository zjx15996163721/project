from crawler.foshan_10 import Foshan
from crawler.chengdu_5 import Chengdu
from crawler.dongwan_9 import Dongwan
from crawler.cixi_8 import Cixi
from crawler.guiyang_13 import Guiyang
from crawler2.hechi_16 import Hechi
from crawler2.guangan_12 import Guangan

from multiprocessing import Process
if __name__ == '__main__':
    foshan_10 = Foshan()
    Process(target=foshan_10.start_crawler).start()

    chengdu_5 = Chengdu()
    Process(target=chengdu_5.start_crawler).start()

    # dongwan_9 = Dongwan()
    # Process(target=dongwan_9.start_crawler).start()

    cixi_8 = Cixi()
    Process(target=cixi_8.start_crawler).start()

    # guiyang_13 = Guiyang()
    # Process(target=guiyang_13.start_crawler).start()

    hechi_16 = Hechi()
    Process(target=hechi_16.start_crawler).start()

    guangan_12 = Guangan()
    Process(target=guangan_12.start_crawler).start()