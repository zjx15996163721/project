from youfangshandai import first_put, second_put, third_put, put_into_mongo
from threading import Thread
from multiprocessing import Process

if __name__ == '__main__':

    # # 优房闪贷
    # #
    # # 获取小区的id
    # con = first_put.Construction()
    # Thread(target=con.get_constructionId).start()
    # # 获取楼栋id
    # build = second_put.BuildingId()
    # Thread(target=build.consume_start).start()
    # # 获取房屋id
    # house = third_put.HouseId()
    # for i in range(10):
    #     Thread(target=house.consume_start).start()
    # # 入库
    # Process(target=put_into_mongo.start_consume).start()
    #
    #
    # # 上海物业
    # #
    # # 放入队列
    # from sh_wuye.get_all_sect_id import produce
    # produce()
    # # 消费 得到build信息,放入队列
    # from sh_wuye.get_building_id import consume_queue as con_build
    # con_build()
    # # 再放入队列
    # produce()
    # # 消费 得到小区详情
    # from sh_wuye.get_detail_info import consume_queue as con_detail
    # for i in range(10):
    #     Process(target=con_detail).start()
    # # 消费楼栋页面
    # from sh_wuye.get_house_num import consume_queue as con_house
    # for i in range(60):
    #     Process(target=con_house).start()


    # 房估估
    #
    # 放入队列
    # from fanggugu.get_all_community_id import produce
    # produce()
    # 消费，得到楼栋信息
    from fanggugu.get_building_info import GetBuild
    from lib.mongo import Mongo

    m = Mongo('192.168.0.235', 27017)
    connection = m.get_connection()
    coll_user = m.get_connection()['fgg']['user_info']
    count = 0
    build = GetBuild()
    for i in coll_user.find():
        user_name = i['user_name']
        print(user_name)
        build.consume_queue(user_name)
    # 消费楼栋，得到房号数据
    from fanggugu.get_house_info import GetHouse
    from lib.mongo import Mongo

    m = Mongo('192.168.0.235', 27017)
    connection = m.get_connection()
    coll_user = m.get_connection()['fgg']['user_info']
    house = GetHouse()
    for i in coll_user.find():
        user_name = i['user_name']
        house.consume_queue(user_name)
