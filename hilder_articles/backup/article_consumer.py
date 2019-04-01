from fenghuang.fenghuang_consumer import Consumer
from wangyi.wangyi_consumer import WangyiConsumer
from weixin.weixin_crawler import weixin_start
from fangtianxia.fangtianxia_start import fangtianxia_start
from meijing.meijing_start import meijing_start
from consumer import Toutiao_Consumer
from threading import Thread
from lib.log import LogHandler
import datetime
import schedule

log = LogHandler('consumer_schedule')

def fangtianxia():
    log.info('{}开始抓取{}'.format(datetime.datetime.now(), 'fangtianxia'))
    Thread(target=fangtianxia_start).start()

def weixin():
    log.info('{}开始抓取{}'.format(datetime.datetime.now(), 'weixin'))
    Thread(target=weixin_start).start()

def meijing():
    log.info('{}开始抓取{}'.format(datetime.datetime.now(), 'meijing'))
    Thread(target=meijing_start).start()

def consumer_run():
    con = Consumer()
    wangyi = WangyiConsumer()
    c = Toutiao_Consumer()
    Thread(target=con.start_consume).start()
    Thread(target=wangyi.start_consume).start()
    Thread(target=c.start_consume).start()
    schedule.every().day.at("16:20").do(weixin)
    schedule.every().day.at("16:20").do(meijing)
    schedule.every().day.at("16:20").do(fangtianxia)
    while True:
        schedule.run_pending()







