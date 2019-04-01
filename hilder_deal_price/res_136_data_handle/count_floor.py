import pymongo
from pymongo import MongoClient
import time
# import threading
# import requests
# import json
import re
import gevent
# import pymongo
"""
这个文件计数的
"""

m = MongoClient(host='192.168.0.136', port=27017)
collection_136 = m['business']['res_esfdealprice']

count = 0
# for i in collection_136.find(limit=5000, no_cursor_timeout=True).sort('_id', pymongo.DESCENDING):

    # if i['houseType'] not in ['公寓', '联列住宅', '别墅未知', '花园住宅']:
    #     count += 1
    #     print(count)
    #     collection_136.delete_one({'_id': i['_id']})


