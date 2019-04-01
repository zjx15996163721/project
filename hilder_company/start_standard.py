from match.job51_standard import job_start_produce,JobConsumer
from match.lagou_standard import lagou_start_produce,LagouConsumer
from match.remain_standard_fields import update_51job_fields,update_lagou_fields
from multiprocessing import Process

if __name__ == '__main__':
    #1.51job队列的生产者
    Process(target=job_start_produce).start()
    #2.51job队列的消费者
    for x in range(4):
        Process(target=JobConsumer().start_consume).start()

    #3.拉钩队列 的生产者
    Process(target=lagou_start_produce).start()
    #4.拉钩队列的消费者
    for x in range(2):
        Process(target=LagouConsumer().start_consume).start()

    #5.由于放入到队列中的时候，不够列表的长度会有剩余，，格式化拉钩和51job剩余的数据
    Process(target=update_lagou_fields).start()
    Process(target=update_51job_fields).start()