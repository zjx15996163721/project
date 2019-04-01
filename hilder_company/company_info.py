import datetime
import yaml
from lib.log import LogHandler
from pymongo import MongoClient
from lib.standardization import standard_city, standard_region
from pymongo.errors import DuplicateKeyError
from lib.standardization import StandarCityError

log = LogHandler(__name__)

setting = yaml.load(open('config.yaml'))
client = MongoClient(host=setting['mongo']['host'],
                     port=setting['mongo']['port'],
                     username=setting['mongo']['user_name'],
                     password=setting['mongo']['password'])
db = client[setting['mongo']['db']]
collection = db[setting['mongo']['collection']]

collection.ensure_index([('company_id', 1), ('company_source', 1)], unique=True, name='id_source_index')


class Company:
    def __init__(self, company_id, company_source, city=None, region=None, address=None, company_name=None,
                 company_short_info=None, company_info=None, business=None, company_size=None,
                 development_stage=None, registration_time=None, registered_capital=None,
                 operating_period=None, url=None):
        self.city = city  # 城市
        self.address = address  # 地址
        self.company_name = company_name  # 公司名
        self.region = region  # 区域
        self.company_short_info = company_short_info  # 公司简介
        self.company_info = company_info  # 公司介绍
        self.business = business  # 行业
        self.company_size = company_size  # 公司规模/人数
        self.development_stage = development_stage  # 发展阶段
        self.registration_time = registration_time  # 注册时间
        self.registered_capital = registered_capital  # 注册资本
        self.operating_period = operating_period  # 经营期限
        self.company_source = company_source  # source
        self.company_id = company_id  # company_id
        self.url = url

    def serialization_info(self):
        """
        :param info:
        :return: data:
        """
        return {key: value for key, value in vars(self).items()}

    def insert_db(self):
        data = self.serialization_info()
        data['crawler_time'] = datetime.datetime.now()
        if data['city'] and data['region']:
            standard_string = data['city'] + data['region']
        else:
            standard_string = None
            # 格式化城市区域
        result, real_city = standard_city(data['city'])
        if result:
            data['fj_city'] = real_city
            try:
                r,real_region = standard_region(real_city, standard_string)
                if r:
                    data['fj_region'] = real_region
                else:
                    data['fj_region'] = None
            except StandarCityError as e:
                log.error(e)
        else:
            data['fj_city'] = None
            data['fj_region'] = None
            # 创建组合索引时使用的代码
        try:
            collection.insert_one(data)
            log.info('插入数据={}'.format(data))
        except DuplicateKeyError as e:
            log.error('该数据已经存在，company_source={},company_id={}'.format(data['company_source'], data['company_id']))