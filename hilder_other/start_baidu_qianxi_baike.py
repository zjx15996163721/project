from baiduqianxi.qianxi import Baiduqianxi
from baike_city.baike import crawler_baike
import schedule

if __name__ == '__main__':
    b = Baiduqianxi()
    print('开始百度百科和迁徙')
    schedule.every().day.at("12:00").do(b.start_consume)
    schedule.every().sunday.at("12:00").do(crawler_baike)
    while True:
        schedule.run_pending()