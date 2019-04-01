"""
todo 通过高德api接口补充经纬度
todo 调用逆地理经纬度代码
"""
import requests

api_key = '2a803d9ba9152132a76dfd6007579adb'


def amap_api(keyword, **kwargs):
    """

    :param keyword:
    :param kwargs:
                city:
    :return:
    """
    url = 'https://restapi.amap.com/v3/place/text?' \
          'keywords={}&city={}&output=json&offset=50&page=1&key={}&extensions=all'. \
        format(keyword, kwargs.get('city'), api_key)
    try:
        r = requests.get(url=url)
    except Exception as e:
        return False, '调用高德地图获取POI请求错误'
    poi_info_list = r.json()['pois']
    if len(poi_info_list) == 0:
        return False, '高德地图没有查询到此keyword'


if __name__ == '__main__':
    amap_api(keyword='朝阳西大望路与广渠路交叉路口的西北角')
