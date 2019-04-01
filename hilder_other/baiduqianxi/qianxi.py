"""
百度迁徙
requests
"""
import requests
import re
from baiduqianxi.city_list import city_id_dict
import datetime
from lib.mongo import Mongo
from queue import Queue
from lib.log import LogHandler
import yaml
import time

setting = yaml.load(open('config.yaml'))

log = LogHandler(__name__)


class Baiduqianxi:
    connect = Mongo(setting['baiduqianxi']['mongo']['host']).connect
    coll = connect[setting['baiduqianxi']['mongo']['db']][setting['baiduqianxi']['mongo']['collection']]

    now_time = datetime.datetime.now()
    today_int = int(now_time.strftime('%Y%m%d'))
    q = Queue(maxsize=0)

    def put_in_queue(self):
        for city_name in city_id_dict:
            city_id = city_id_dict[city_name]
            self.q.put((city_name, city_id))

    def start_consume(self):
        count = 0
        self.put_in_queue()
        while not self.q.empty():
            city_info = self.q.get()
            city_name = city_info[0]
            city_id = city_info[1]
            try:
                type_ = 'move_in'
                city = city_name
                time_str = str(self.today_int)
                url = 'http://huiyan.baidu.com/migration/api/cityrank?dt=city&id=' + city_id + '&type=' + type_ + '&date=' + time_str
                res_in = requests.get(url)
                time.sleep(10)
                in_info = re.search(r'\[(.*?)\]', res_in.text).group()
                in_list = eval(in_info)
                in_all_list = []
                for i in in_list:
                    in_all_list.append(i)
                type_ = 'move_out'
                url = 'http://huiyan.baidu.com/migration/api/cityrank?dt=city&id=' + city_id + '&type=' + type_ + '&date=' + time_str
                res_out = requests.get(url)
                time.sleep(10)
                out_info = re.search(r'\[(.*?)\]', res_out.text).group()
                out_list = eval(out_info)
                out_all_list = []
                for i in out_list:
                    out_all_list.append(i)
                count += 1
                log.info('count={},城市={}'.format(count, city_name))
                data = {
                    'city': city_name,
                    'date': int(time_str),
                    'insert_time': datetime.datetime.now(),
                    'in': in_all_list,
                    'out': out_all_list,
                }
                if not in_all_list and not in_all_list:
                    log.info('迁入和迁出为空,{}'.format(city))
                else:
                    log.info('插入一条数据,{}'.format(data))
                    self.coll.insert_one(data)
                self.q.task_done()
            except Exception as e:
                log.error('错误,e={}'.format(e))
                self.q.put(city_name)
