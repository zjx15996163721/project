import mitmproxy.http
from pymongo import MongoClient
import json


class Counter:
    def __init__(self):
        m = MongoClient(host='114.80.150.196',
                        port=27777,
                        username='goojia',
                        password='goojia7102')
        self.collection = m['amap']['amap_road_adb']

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if 'mapapi/poi/infolite' in flow.request.url:
            text = flow.response.get_text()
            self.collection.insert_one({'poi': json.loads(text), 'url': flow.request.url})


addons = [
    Counter()
]
