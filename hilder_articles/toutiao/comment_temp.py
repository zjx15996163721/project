from lib.mongo import Mongo
import yaml

setting = yaml.load(open('config_local.yaml'))

def serialization_info(info):
    """

    :param info:
    :return: data:
    """
    data = {}
    for key, value in vars(info).items():
        if key is 'coll':
            continue
        data[key] = value
    return data


class Comment_url():
    def __init__(self, comment_count=None, group_id=None, crawler_time=None):
        self.comment_count = comment_count
        self.group_id = group_id
        self.crawler_time = crawler_time

        self.coll = Mongo(setting['mongo']['host'], setting['mongo']['port'])

    def insert_db(self):
        db = setting['mongo']['db_name']
        coll = setting['mongo']['url_code']
        self.coll = self.coll[db][coll]
        data = serialization_info(self)
        self.coll.create_index([("crawler_time", 1)], expireAfterSeconds=12 * 60 * 60)
        self.coll.insert_one(data)
        print('插入一条数据', data)

    def to_dict(self):
        data = serialization_info(self)
        return data

    def dict_to_attr(self, dict_data):
        """
        传递字典返回文章对象
        :param dict_data:
        :return:
        """
        for key, value in dict_data.items():
            if not hasattr(self, key):
                print('not has key:', key)
                continue
            setattr(self, key, value)
        return self
