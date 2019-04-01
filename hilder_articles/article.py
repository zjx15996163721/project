from lib.mongo import Mongo
import yaml
from lib.log import LogHandler
import datetime

setting = yaml.load(open('config_local.yaml'))
log = LogHandler("article_insert")

mongo = Mongo(setting['mongo']['host'], setting['mongo']['port'])
client = mongo.connect
coll = client[setting['mongo']['db_name']][setting['mongo']['coll_comm']]


def serialization_info(info):
    """

    :param info:
    :return: data:
    """
    data = {}
    for key, value in vars(info).items():
        if key is 'connect':
            continue
        data[key] = value
    return data


class Article:

    def __init__(self, source, url=None, title=None, body=None, article_id=None, post_time=None, title_img=None,
                 comment_count=None, like_count=None, author=None, read_num=None, crawler_time=None,
                 organization_author=None, city=None, source_detail=None, category=None, tag=None, desc=None,
                 s_post_time=None):
        self.source = source  # 文章来源
        self.url = url  # 链接
        self.title = title  # 标题
        self.body = body  # 正文
        self.article_id = article_id  # 文章id
        self.title_img = title_img  # 列表页的图片/封面
        self.comment_count = comment_count  # 评论数 num
        self.like_count = like_count  # 点赞数 num
        self.read_num = read_num  # 阅读量 num
        self.author = author  # 作者
        self.post_time = post_time  # 文章发布时间 str
        self.crawler_time = crawler_time  # 抓取时间
        self.status = 0
        self.organization_author = organization_author
        self.city = city
        self.source_detail = source_detail  # 文章详细来源网站
        self.category = category  # 分类
        self.tag = tag  # 标签
        self.desc = desc  # 简介
        self.s_post_time = s_post_time

    def insert_db(self):
        data = serialization_info(self)
        data["crawler_time"] = datetime.datetime.now()
        if '图片替换失败！' in data['body']:
            log.error('{}图片替换失败'.format(data['source']))
        else:
            coll.insert_one(data)

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


if __name__ == '__main__':
    # print(setting['mongo']['host'],
    #       setting['mongo']['port'],
    #       setting['mongo']['db_name'],
    #       setting['mongo']['coll_comm'])
    a = Article(source='toutiao')
    a.insert_db()
