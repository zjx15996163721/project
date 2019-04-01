# from youda_res.res_selenium import start_second, start_new_house, start_land
from youda_res.res_second_data_format_to136 import FormatSecond
from youda_res.res_newhouse_data_format import FormatNewHouse
from youda_res.res_second_data_to43 import ResData

if __name__ == '__main__':

    """
    二手成交
    
    需先启动 mitmproxy
    启动方法: 虚拟环境 mitmdump -s youda_res/mitmproxy_second.py
    """
    # 启动selenium
    # start_second()

    # # 数据处理入136库
    # second = FormatSecond('澜斯')
    # # 添加格式化城市，区域，小区名，经纬度，坐标，楼层，总楼层
    # second.add_fj_name()
    # second.add_lng()
    # second.add_floor()
    # 入库
    # second.insert_136()

    # 数据处理入43库
    res = ResData('澜斯')
    res.match_house_num()
    res.insert_43()

    """
    新房成交
    
    需先启动 mitmproxy
    启动方法: 虚拟环境 mitmdump -s youda_res/mitmproxy_newhouse.py
    """
    # 启动selenium
    # start_new_house()

    # 数据处理入136库
    # newhouse = FormatNewHouse('澜斯')
    # newhouse.start()

    # 数据处理入43库
    """
    土地成交
    
    需先启动 mitmproxy
    启动方法: 虚拟环境 mitmdump -s youda_res/mitmproxy_land.py
    """
    # 启动selenium
    # start_land()

    # 数据处理入库
