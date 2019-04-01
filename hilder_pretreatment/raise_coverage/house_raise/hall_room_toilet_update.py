from raise_coverage import *

update_mongo = MongoClient('mongodb://{username}:{password}@{host}:{port}'.format(**house_config), connect=False)
update_col = update_mongo[house_config['db']][house_config['collection']]


class Direction:

    # 判断是否为有效朝向
    @classmethod
    def format_room_info(cls, room_info, info=None):
        '''
        :param room_info: 房子信息，几室几厅
        :param info: 指定room_info传进来的信息为room、hall、toilet中的哪一个，默认为几室几厅
        :return: 室、厅、卫
        '''
        shuzi = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '十': '1', }
        for word in room_info:
            if word in shuzi:
                room_info = room_info.replace(word, shuzi[word])

        if info == 'room':
            room = re.search(r'(\d+)', room_info)
            if room and int(room.group(1)) > 0 and int(room.group(1)) < 20:
                return {'room': room.group(1)}
        elif info == 'hall':
            hall = re.search(r'(\d+)', room_info)
            if hall and int(hall.group(1)) > 0 and int(hall.group(1)) < 10:
                return {'hall': hall.group(1)}
        elif info == 'toilet':
            toilet = re.search(r'(\d+)', room_info)
            if toilet and int(toilet.group(1)) > 0 and int(toilet.group(1)) < 10:
                return {'hall': toilet.group(1)}
        else:
            room = re.search(r'(\d+)[室房]', room_info)
            hall = re.search(r'(\d+)[厅]', room_info)
            toilet = re.search(r'(\d+)[卫厕]', room_info)
            room_hall_toilet = {}
            try:
                room_hall_toilet['room'] = int(room.group(1))
            except:
                pass
            try:
                room_hall_toilet['hall'] = int(hall.group(1))
            except:
                pass
            try:
                room_hall_toilet['toilet'] = int(toilet.group(1))
            except:
                pass
            if len(room_hall_toilet) > 0:
                return room_hall_toilet

    # 根据楼栋号更新整栋楼的楼号
    @classmethod
    def update_hall_room_toilet(cls, city, region, name, house_num, room_info, room_info_source, room_num=None,
                                info=None, house_num_unit='--'):
        '''
        :param city: 城市
        :param region: 区域
        :param name: 小区名
        :param house_num: 楼栋号
        :param direction: 朝向
        :param direction_source: 朝向来源
        :param room_num: 房号
        '''
        query = {'city': city, 'region': region, 'name': name, 'house_num': house_num, 'house_num_unit': house_num_unit}
        if room_num:
            query = {'city': city, 'region': region, 'name': name, 'house_num': house_num,
                     'house_num_unit': house_num_unit, 'room_num': room_num}

        # 判断来源朝向是否有效
        house_info = cls.format_room_info(room_info, info)
        if house_info:
            house_list = list(update_col.find(query))
            if len(house_list) > 0:
                print(query, '***更新')
                for house in house_list:
                    for house_info_key in house_info:
                        if house_info_key not in house or house[house_info_key] in [None, '', -1]:
                            # 初始化一个字段来源list
                            columns_source = []
                            try:
                                columns_source = house['columns_source']
                            except:
                                pass

                            if house.get('from', None) != room_info_source:
                                if len(columns_source) > 0:
                                    for column in columns_source:
                                        if house_info_key in column:
                                            columns_source.remove(column)
                                columns_source.append({house_info_key: room_info_source, 'u_time': datetime.utcnow()})
                            update_col.update_one({'_id': house['_id']},
                                                  {'$set': {house_info_key: house_info[house_info_key],
                                                            'columns_source': columns_source,
                                                            'm_date': datetime.utcnow()}})


if __name__ == '__main__':
    print('a')
    # Direction.update_hall_room_toilet('深圳','龙岗', '悦城花园','7','4室2厅2卫1厨','小资家')
