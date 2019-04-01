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

class Comments():
    def __init__(self,article_id=None,text=None,comment_id=None,user_name=None,user_id=None,create_time=None,good_count=None):
        self.comment_text = text
        self._id = comment_id
        self.user_name = user_name
        self.user_id = user_id
        self.create_time = create_time
        self.good_count = good_count
        self.article_id = article_id
        self.coll = Mongo(setting['mongo']['host'], setting['mongo']['port'], setting['mongo']['db_name'],
                          setting['mongo']['comments']).get_collection_object()

    def insert_db(self):
        data = serialization_info(self)
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
