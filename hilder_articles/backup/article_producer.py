from fenghuang.fenghuang_producer import Fenghuang
from wangyi.wangyi_producer import Wangyi
from toutiao.toutiao_api import Toutiao
from threading import Thread
import schedule
import time
from lib.log import LogHandler
import datetime

log = LogHandler("producer_schedule")
def fenghuang():
    fen = Fenghuang()
    log.info('{}开始抓取{}url'.format(datetime.datetime.now(), 'fenghuang'))
    Thread(target=fen.start_crawler).start()

def wangyi():
    wangyi = Wangyi()
    log.info('{}开始抓取{}url'.format(datetime.datetime.now(),'wangyi'))
    Thread(target=wangyi.start_crawler).start()

def toutiao():
    toutiao = Toutiao()
    log.info('{}开始抓取{}url'.format(datetime.datetime.now(), 'toutiao'))
    Thread(target=toutiao.start_crawler).start()

def producer_run():
    schedule.every().day.at("18:30").do(fenghuang)
    schedule.every().day.at("18:30").do(wangyi)
    schedule.every().day.at("11:20").do(toutiao)

    while True:
        schedule.run_pending()
        time.sleep(1)


