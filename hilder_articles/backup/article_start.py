from backup.article_consumer import consumer_run
from backup.article_producer import producer_run
from multiprocessing import Process
if __name__ == '__main__':
    # 忽略此句
    Process(target=consumer_run).start()
    Process(target=producer_run).start()
