from raise_coverage import *

update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**house_config), connect=False)
update_col = update_mongo[house_config['db']][house_config['collection']]

class Direction:

    _true_words = ["东北", "西北", "东南", "西南","南北","东西","东", "南", "西", "北" ]

    # 判断是否为有效朝向
    @classmethod
    def format_direction(cls, direction):
        '''
        :param direction: 朝向
        :return: 有效朝向
        '''
        word_list = []
        for k in ['东','南','西','北']:
            if k in str(direction):
                word_list.append(k)

        if len(word_list) > 0 and ''.join(word_list) in cls._true_words:
            return ''.join(word_list)

    # 根据楼栋号更新整栋楼的楼号
    @classmethod
    def update_direction(cls, city, region, name, house_num, direction, direction_source, room_num=None):
        '''
        :param city: 城市
        :param region: 区域
        :param name: 小区名
        :param house_num: 楼栋号
        :param direction: 朝向
        :param direction_source: 朝向来源
        :param room_num: 房号
        '''
        query = {'city': city, 'region': region, 'name': name, 'house_num': house_num}
        if room_num:
            query = {'city': city, 'region': region, 'name': name, 'house_num': house_num, 'room_num': room_num}

        # 判断来源朝向是否有效
        direction = cls.format_direction(direction)
        if direction:
            house_list = list(update_col.find(query))
            if len(house_list) > 0:
                print(query, '***更新')
                for house in house_list:
                    if 'direction' not in house or house['direction'] not in cls._true_words:

                        # 初始化一个字段来源list
                        columns_source = []
                        try:
                            columns_source = house['columns_source']
                        except:
                            pass

                        if house.get('from', None) != direction_source:
                            if len(columns_source) > 0:
                                for column in columns_source:
                                    if 'direction' in column:
                                        columns_source.remove(column)
                            columns_source.append({'direction':'小资家', 'u_time':datetime.utcnow()})

                        update_col.update_one({'_id':house['_id']},
                                              {'$set':{'direction':direction, 'columns_source':columns_source, 'm_date':datetime.utcnow()}})


