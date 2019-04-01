from auction_final.auction_list import Gdlist
from auction_final.ali import Ali
from auction_final.swagger import Swagger


if __name__ == '__main__':
    while True:
        jingdong = Gdlist()
        ali = Ali()
        swagger = Swagger()
        try:
            print('开始抓取京东拍卖')
            jingdong.start_crawler()
            print('开始抓取阿里拍卖')
            ali.start_crawler()
            print('开始请求，调用接口')
            swagger.request()
        except Exception as e:
            print(e)
            continue
