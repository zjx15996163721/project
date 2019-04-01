from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import json


class Monbbit():
    """
        将MongoDB的字段放到rabbit中
            :param db(str): 数据库名    (must)
            :param coll(str): 表名    (must)
            :param queue(str): 队列名  (must)
            :param args(str): 字段名，多个字段直接跟在后面
            :param m_host(str): mongo的地址
            :param m_port(int): mongo的端口
            :param r_host(str): rabbit的地址
            :param r_port(str): rabbit的端口
    """

    def __init__(self, db, coll, queue, *args, m_host='192.168.0.235', m_port=27017, r_host='192.168.0.190',
                 r_port=5673):
        self.db = db
        self.coll = coll
        self.queue = queue
        self.m_host = m_host
        self.m_port = m_port
        self.r_host = r_host
        self.r_port = r_port
        self.args = args
        self.data = {}

    def connect_mongo(self):
        m = Mongo(self.m_host, self.m_port,user_name='fangjia',password='fangjia123456')
        return m.connect[self.db][self.coll]

    def connect_rabbit(self):
        r = Rabbit(self.r_host, self.r_port)
        return r.get_channel()

    def put_rabbit(self):
        coll = self.connect_mongo()
        channel = self.connect_rabbit()
        channel.queue_declare(queue=self.queue)
        for i in coll.find({}, no_cursor_timeout=True):
            try:
                for args in self.args:
                    self.data[args] = i[args]
                print(self.data)
                channel.basic_publish(exchange='',
                                      routing_key=self.queue,
                                      body=json.dumps(self.data))
            except Exception as e:
                print('输入的字段数据库中不存在', e)
                break


if __name__ == '__main__':
    m = Monbbit('friends', 'xiaozijia_build_fast_copy', 'xiaozijia_build', 'ConstructionId', 'IdSub',
                m_host='114.80.150.196', r_host='127.0.0.1'
                )
    m.put_rabbit()
