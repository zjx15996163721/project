import gevent
from gevent import monkey
monkey.patch_all()
from raise_coverage import *
from raise_coverage.mongo_config import district_complete, temporary_config
from raise_coverage.district_raise.estate_charge_update import EstateCharge
from raise_coverage.district_raise.household_count_update import HouseholdCount
import pandas as pd

from_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**district_complete), connect=False)
from_col = from_mongo[district_complete['db']][district_complete['collection']]

update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**temporary_config), connect=False)
update_col = update_mongo[temporary_config['db']][temporary_config['collection']]


def update_byid(i):
    district = update_col.find_one({'_id':ObjectId(i['fj_id'])}, {'household_count':1, 'estate_charge':1})
    if district:
        updata_dict = {}
        update_flag = []
        if 'update_flag' in district:
            update_flag = district['update_flag']
        if 'household_count' not in district or district['household_count'] in [None, "", -1, 0]:
            household_count = HouseholdCount.format_household_count(i['household_count'])
            # print(household_count)
            if household_count:
                updata_dict['household_count'] = household_count
                update_flag.append('household_count')
        if 'estate_charge' not in district or district['estate_charge'] in [None, "","0.0"]:
            estate_charge = EstateCharge.format_estate_charge(i['estate_charge'])
            if estate_charge:
                updata_dict['estate_charge'] = estate_charge
                update_flag.append('estate_charge')
        if len(update_flag) > 0:
            print(update_flag)
            updata_dict['update_flag'] = update_flag
            update_col.update_one({'_id':ObjectId(i['fj_id'])},{'$set':updata_dict})


if __name__ == '__main__':

    # n = 0
    # data_list = []
    # for d in from_col.find({'source':'loupan'}, {'household_count': 1, 'estate_charge': 1, 'fj_id':1}):
    #     n += 1
    #     if n%1000 == 0:
    #         print(n)
    #     if 'fj_id' in d:
    #         update_byid(d)
    data_list = list(update_col.find({'estate_charge':{'$nin':[None,0,"","0.0"]}},
                                {'city':1,'region':1,'name':1,'estate_type2':1, 'estate_charge':1, 'update_flag':1}))

    df = pd.DataFrame(data_list)
    df.to_excel('e:/huangcunliang/20181127/' + 'estate_charge1.xlsx')
