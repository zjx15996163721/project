from raise_coverage import *
from raise_coverage.mongo_config import temporary_config


update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**temporary_config), connect=False)
update_col = update_mongo[temporary_config['db']][temporary_config['collection']]

class FinishDate:

    @classmethod
    def format_finish_building_date(cls, date):
        return date[:10]

    @classmethod
    def update_finish_building_date(cls, fj_id, finish_date):
        if finish_date in ['',None]:
            return '错误数据'

        fa_finishbuilding_date = cls.format_finish_building_date(finish_date)
        district = update_col.find_one({'_id':ObjectId(fj_id)})
        if district:
            if 'finish_building_date' not in district or district['finish_building_date'] in ['',None,-1,'-1']:
                print(fa_finishbuilding_date)
                update_col.update_one({'_id':ObjectId(fj_id)},{'$set':{'finish_building_date':fa_finishbuilding_date,
                                                                       'm_date':datetime.utcnow()}})
                print('update succeeful')

