from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from lib.log import LogHandler

# 创建对象的基类:
Base = declarative_base()
log = LogHandler(__name__)
engine = create_engine('mysql+pymysql://root:goojia7102@114.80.150.196:3336/auction_config',pool_recycle=5)
DBSession = sessionmaker(bind=engine)


class CityAuction(Base):
    # 表的名字:
    __tablename__ = 'city_auction'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    code = Column(String(100))
    province = Column(String(50))
    province_id = Column(String(50))
    city = Column(String(50))
    city_id = Column(String(50))
    region = Column(String(50))
    source = Column(String(50))

    def __repr__(self):
        return "<City_auction(code='%s', province='%s', city='%s', region='%s',province_id='%s',city_id='%s')>" % (
            self.code, self.province, self.city, self.region, self.province_id, self.city_id)


class TypeAuction(Base):
    # 表的名字:
    __tablename__ = 'type_auction'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    auction_type = Column(String(50))
    html_type = Column(String(50))
    source = Column(String(50))

    def __repr__(self):
        return "<Type_auction(code='%s', auction_type='%s', html_type='%s')>" % (
            self.code, self.auction_type, self.html_type)


def inquire(class_base, filter_source):
    """
        查询  通过类名，过滤条件，返回一个一条数据的对象
        :param class_base: 数据库类名
        :param filter_source: 过滤的source
        :return: 一条数据的对象
    """
    session = DBSession()
    return session.query(class_base).filter(class_base.source == filter_source).all()


def insert_type(data_obj, type_class):
    try:
        session = DBSession()
        source = data_obj.source
        code = data_obj.code
        if not session.query(type_class).filter(type_class.code == code, type_class.source == source).first():
            session.add(data_obj)
            session.commit()
            session.close()
            log.info('插入成功,data={}'.format(vars(data_obj).items()))
        else:
            log.info('数据已存在')
    except Exception as e:
        return log.error('插入失败,data={},e="{}"'.format(data_obj, e))


def delete_type(type_class, filter_source):
    try:
        session = DBSession()
        session.query(type_class).filter(type_class.source == filter_source).delete(synchronize_session=False)
        session.commit()
        log.info('删除成功,source={}'.format(filter_source))
    except Exception as e:
        return log.error('删除失败,e="{}"'.format(e))


Base.metadata.create_all(engine)

if __name__ == '__main__':
    # ************插入数据**************
    # data = {'12727': ('机动车', '车'),
    #          '12728': ('住宅用房', '住宅'),
    #          '13809': ('商品用房', '商铺'),
    #          '13817': ('工业用房', '厂房'),
    #          '13810': ('其他用房', '其他'),
    #          '12729': ('股权', '证券'),
    #          '13812': ('债券', '证券'),
    #          '12730': ('土地', '土地'),
    #          '12731': ('林权', '证券'),
    #          '12734': ('矿权', '证券'),
    #          '13813': ('机械设备', '其他'),
    #          '12732': ('工程', '其他'),
    #          '13816': ('船舶', '其他'),
    #          '12733': ('无形资产', '其他'),
    #          '13814': ('其他财产', '其他'),
    #          '13811': ('其他交通运输工具', '其他'), }
    # source = 'jingdong'
    # for i in data:
    #     # new_user = CityAuction(code=i, city=data[i], source=source)
    #     new_user = TypeAuction(code=i, auction_type=data[i][1], html_type=data[i][0], source=source)
    #     # 插入方法
    #     insert_type(new_user, TypeAuction)
    # **************查询****************
    data = inquire(CityAuction, 'rmfysszc')
    print(data)
    # **************删除****************
    # delete_type(TypeAuction, 'zhupaiwang')
