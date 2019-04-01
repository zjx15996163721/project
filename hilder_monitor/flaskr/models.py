from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

# 创建对象的基类
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False)  # 用户名
    password = Column(String(64), nullable=False)  # 密码


class MonitorProject(Base):
    __tablename__ = 'monitor_project'

    id = Column(Integer, primary_key=True)  # 设置为主键
    project_name = Column(String(2000), nullable=False, unique=True)  # 创建索引,不为空

    def serialization_info(self):
        """
        对象转字典
        :return: data:
        """
        data = {}
        for key, value in vars(self).items():
            data[key] = value
        del data['_sa_instance_state']
        return data


class MonitorProjectInfo(Base):
    __tablename__ = 'monitor_project_info'  # 表名

    id = Column(Integer, primary_key=True)  # 设置为主键
    project_id = Column(Integer)
    total_quantity = Column(Integer)  # 数据总量
    crawler_quantity = Column(Integer)  # 抓取总量
    result_quantity = Column(Integer)  # 入库总量

    crawler_start_time = Column(Date)  # 开始抓取时间
    crawler_end_time = Column(Date)  # 结束时间

    author = Column(String(2000))  # 作者
    partner = Column(String(2000))  # 协助者

    def serialization_info(self):
        """
        对象转字典
        :return: data:
        """
        data = {}
        for key, value in vars(self).items():
            data[key] = value
        del data['_sa_instance_state']
        return data
