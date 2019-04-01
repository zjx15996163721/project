from raise_coverage import *
from raise_coverage.mongo_config import temporary_config

update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**temporary_config), connect=False)
update_col = update_mongo[temporary_config['db']][temporary_config['collection']]

class HouseholdCount:

    @classmethod
    def format_household_count(cls, household_count):
        household_count_num = re.findall(r'([0-9]+)', str(household_count))
        if len(household_count_num) == 1:
            try:
                if int(household_count_num[0]) > 0:
                    return int(household_count_num[0])
            except:
                pass

    @classmethod
    def update_finish_building_date(cls, fj_id, household_count):
        if household_count in [None,"","0","-1",0,1]:
            return "...户数格式错误"
        fa_household_count = cls.format_household_count(household_count)
        if household_count:
            district = update_col.find_one({'_id':ObjectId(fj_id)})
            if district:
                if 'household_count' not in district or district['household_count'] in ['', None, -1, '-1']:
                    print(fa_household_count)
                    # update_col.update_one({'_id':ObjectId(fj_id)},{'$set':{'household_count':fa_household_count, 'm_date':datetime.utcnow()}})

