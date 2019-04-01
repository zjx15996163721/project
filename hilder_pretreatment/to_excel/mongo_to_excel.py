import gevent
from gevent import monkey

monkey.patch_all()
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from district_match.match_seaweed import match
import re


class MongoToexcel:

    def __init__(self, host, port, db, col, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.col = col
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.match_list = []
        self.columns_order = []

    def mongo_collection(self):
        if self.username:
            URL = "mongodb://{}:{}@{}:{}".format(self.username, self.password, self.host, self.port)
        else:
            URL = "mongodb://{}:{}".format(self.host, self.port)
        mongo = MongoClient(URL, connect=False)
        return mongo[self.db][self.col]

    def to_match(self, data):
        collection = self.mongo_collection()
        city = data.get(data['name_dict'].get('城市'))
        region = data.get(data['name_dict'].get('区域'), '')
        name = data.get(data['name_dict'].get('名称'), '')
        address = data.get(data['name_dict'].get('地址'), '')

        if name == '' and address == '':
            print('..{}无法识别到名称或地址'.format(data))

        if name:
            match_info = match(city,
                               **{'region': region, 'keyword': name, 'category': data['category']})
            if match_info:
                if '精确匹配' in match_info['flag']:
                    data['match_flag'] = '精确匹配'
                    print('精确匹配')
                    collection.update_one({'_id': data['_id']},
                                          {'$set': {'match_flag': match_info['flag'], 'fj_id': match_info['_id'],
                                                    'fjName': match_info['mname']}})
                else:
                    data['匹配区域(名称)'], data['匹配名称(名称)'] = match_info['mregion'], match_info['mname']
                    data['匹配地址(名称)'], data['匹配名称别名(名称)'], data['匹配地址别名(名称)'] = match_info['maddress'], match_info[
                        'malias'], match_info['maddralias']
                    data['匹配id(名称)'] = match_info['_id']
                    collection.update_one({'_id': data['_id']},
                                          {'$set': {'match_flag': match_info['flag']}})

        if address and re.search(r'\d+(号|弄|支|支弄)', str(address)):
            match_info = match(city,
                               **{'region': region, 'keyword': name})
            if match_info:

                if '精确匹配' in match_info['flag']:
                    data['match_flag'] = '精确匹配'
                    print('精确匹配')
                    collection.update_one({'_id': data['_id']},
                                          {'$set': {'match_flag': match_info['flag'], 'fj_id': match_info['_id'],
                                                    'fjName': match_info['mname']}})

                else:

                    data['匹配区域(地址)'], data['匹配名称(地址)'] = match_info['mregion'], match_info['mname']
                    data['匹配地址(地址)'], data['匹配名称别名(地址)'], data['匹配地址别名(地址)'] = match_info['maddress'], match_info[
                        'malias'], match_info['maddralias']
                    data['匹配id(地址)'] = match_info['_id']
                    collection.update_one({'_id': data['_id']},
                                          {'$set': {'match_flag': match_info['flag']}})

        if '匹配区域(地址)' in data or '匹配区域(名称)' in data:
            print(data)
            self.match_list.append(data)
        else:
            if 'match_flag' not in data:
                self.match_list.append(data)
                collection.find_one_and_update({'_id':data['_id']}, {'$set':{'match_flag':'未匹配上'}})

    def match_data(self, data_list, name_dict, category):
        to_match_list = []
        for data in data_list:
            data['name_dict'] = name_dict
            data['category'] = category
            to_match_list.append(data)
            if len(to_match_list) == 50:
                tasks = [gevent.spawn(self.to_match, d) for d in to_match_list]
                gevent.joinall(tasks)
                to_match_list.clear()
        if len(to_match_list) > 0:
            tasks = [gevent.spawn(self.to_match, d) for d in to_match_list]
            gevent.joinall(tasks)

    def to_excel(self, **kwargs):
        '''

        :param kwargs: 不传则默认全表全字段，按原字段名导出
                    query: 查询条件，mongo查询语法，如不传默认查询全部数据
                    columns：字段对应字典，如不传默认所有字段按原字段导出
                    filename: 导出文件名称及路径，如不传名称默认为mongo表明+当天日期，路径默认当前路径
                    if_match: 是否需要对所选数据与库中小区写字楼等进行匹配，此时columns为必传，
                              且城市区域名称地址必需对应关键字城市、区域、名称、地址
                    category: 选择的数据的类型，office写字楼、shop商铺、property小区、company公司,需要进行匹配才需要传

        :return:
        '''

        collection = self.mongo_collection()

        query = kwargs.get('query', {})
        num = collection.count_documents(query)
        if num > 1500000 and kwargs.get('out_put') is not True:
            print('...所查询数据过多，建议按条件分批导出，若执意导出，请添加out_put为True')
            return False

        filename = kwargs.get('filename', None)
        if not filename:
            filename = str(self.col) + str(datetime.now())[:10].replace('-', '')

        defined_columns = kwargs.get('columns', {'_id': 0})
        columns = {k: 1 for k in defined_columns if k != '_id'}
        self.columns_order = [k for k in defined_columns.values()]
        print(self.columns_order)
        if kwargs == {}:
            df = pd.DataFrame(list(collection.find({})))
            if len(df) == 0:
                print('...查询无数据，请确认数据库是否正确')
                return False
            df['_id'] = df['_id'].apply(lambda x: str(x))
            df.to_excel('{}.xlsx'.format(filename), encoding='utf-8', index=False)
            return True

        data_list = list(collection.find(query, columns))
        if len(data_list) == 0:
            print('...查询无数据，请确认数据库或查询条件')
            return False

        if kwargs.get('if_match') == 'yes':
            name_ditc = {v: k for k, v in defined_columns.items() if k != '_id'}
            self.columns_order += ['匹配id(名称)', '匹配区域(名称)', '匹配名称(名称)', '匹配地址(名称)', '匹配名称别名(名称)', '匹配地址别名(名称)',
                                   '匹配id(地址)', '匹配区域(地址)', '匹配名称(地址)', '匹配地址(地址)', '匹配名称别名(地址)', '匹配地址别名(地址)']
            self.match_data(data_list, name_ditc, kwargs['category'])
            data_list = self.match_list

        df = pd.DataFrame(data_list)
        try:
            df['_id'] = df['_id'].apply(lambda x: str(x))
        except:
            pass
        if kwargs.get('columns'):
            df.rename(columns=kwargs['columns'], inplace=True)
        dforder = df.loc[:, self.columns_order]
        dforder.to_excel('{}.xlsx'.format(filename), encoding='utf-8', index=False)


if __name__ == '__main__':
    mx = MongoToexcel('114.80.150.196', 27777, 'company', 'office_building', username='goojia',
                      password='goojia7102')
    mx.to_excel(query={},
                columns={'_id':'_id','city': '城市', 'region': '区域', 'name': '名称', 'address': '地址'},
                category='office',
                if_match='yes')

