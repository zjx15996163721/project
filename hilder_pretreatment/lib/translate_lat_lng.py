"""
高德经纬度转百度经纬度
"""
import math

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


def gd_to_bd(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    高德——>百度
    :param lng:高德坐标经度
    :param lat:高德坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd_to_gd(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


if __name__ == '__main__':
    # 高德转百度
    baidu_lng, baidu_lat = gd_to_bd(87.351218, 43.947248)
    print(baidu_lng, baidu_lat)
    # 百度转高德
    gaode_lng, gaode_lat = bd_to_gd(baidu_lng, baidu_lat)
    print(gaode_lng, gaode_lat)
