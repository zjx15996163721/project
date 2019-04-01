from raise_coverage import *
from raise_coverage.mongo_config import temporary_config

update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**temporary_config), connect=False)
update_col = update_mongo[temporary_config['db']][temporary_config['collection']]


class EstateCharge:

    @classmethod
    def format_estate_charge(cls, estate_charge):
        estate_charge_num = re.findall(r'([0-9]+\.[0-9]+)', str(estate_charge))
        if len(estate_charge_num) == 1:
            return estate_charge_num[0]

    @classmethod
    def update_estate_charge(cls, fj_id, estate_charge):
        if estate_charge in [None, "","0","-1"]:
            return "...户数格式错误"
        fa_estate_charge = cls.format_estate_charge(estate_charge)
        if fa_estate_charge:
            district = update_col.find_one({'_id': ObjectId(fj_id)})
            if district:
                if 'estate_charge' not in district or district['estate_charge'] in ['', None, -1, '-1']:
                    print(fa_estate_charge)
                    # update_col.update_one({'_id': ObjectId(fj_id)},
                    #                       {'$set': {'household_count': fa_estate_charge, 'm_date': datetime.utcnow()}})
