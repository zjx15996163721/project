import requests
import gevent
from gevent import monkey
import time

monkey.patch_all()

# url_list = ['https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7']
url_list = [
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF1000%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF991%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF992%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF993%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF994%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF995%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF996%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF997%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF998%E5%8F%B7',
    'https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=15&city=310000&geoobj=121.34105%7C31.207259%7C121.37431%7C31.235443&keywords=%E9%87%91%E9%92%9F%E8%B7%AF999%E5%8F%B7', ]

proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
    "host": "http-proxy-sg2.dobel.cn",
    "port": "9180",
    "account": 'FANGJIAHTTTEST1',
    "password": "HGhyd7BF",
}
proxies = {"https": proxy,
           "http": proxy}


def async_message(_url):
    try:
        result = requests.get(_url, timeout=2, proxies=proxies)
        # print(result.content.decode())
        if result.json()['status'] != "1":
            print('错误')
    except Exception as e:
        print('错误')


def callback():
    jobs = [gevent.spawn(async_message, _url) for _url in url_list]
    gevent.wait(jobs)


if __name__ == '__main__':
    while True:
        c = time.time()
        print('------------------')
        callback()
        print('时间={}'.format(time.time() - c))