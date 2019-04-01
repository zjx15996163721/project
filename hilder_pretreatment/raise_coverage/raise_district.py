import gevent
from gevent import monkey

monkey.patch_all()
from raise_coverage import *
from raise_coverage.mongo_config import xiaozijia_comm_config, temporary_config, xzj_yd_res_fj_config
from raise_coverage.district_raise.finish_building_date_update import FinishDate

from_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**xiaozijia_comm_config), connect=False)
from_col = from_mongo[xiaozijia_comm_config['db']][xiaozijia_comm_config['collection']]

xzj_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**xzj_yd_res_fj_config), connect=False)
xzj_col = xzj_mongo[xzj_yd_res_fj_config['db']][xzj_yd_res_fj_config['collection']]


def update_data(i):
    if i['CompletionDate'] not in ['', None]:
        xzj_fj = xzj_col.find_one({'xzj_ConstructionId': i['ConstructionId']})
        if xzj_fj and xzj_fj['city'] in ['上海', '合肥', '无锡']:
            fj_id = xzj_fj['fj_id']
            # print(i['CompletionDate'], fj_id)
            FinishDate.update_finish_building_date(fj_id, i['CompletionDate'])


if __name__ == '__main__':
    n = 0
    data_list = []
    for d in from_col.find({}, {'ConstructionId': 1, 'CompletionDate': 1}):
        n += 1
        print(n)
        if d['CompletionDate'] not in ['', None]:
            data_list.append(d)
        if len(data_list) == 50:
            tasks = [gevent.spawn(update_data, data) for data in data_list]
            gevent.joinall(tasks)
            data_list.clear()
    if len(data_list) > 0:
        tasks = [gevent.spawn(update_data, data) for data in data_list]
        gevent.joinall(tasks)
