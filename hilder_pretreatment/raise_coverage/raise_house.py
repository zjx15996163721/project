from raise_coverage.house_raise.direction_update import Direction
from raise_coverage import MongoClient
import pandas as pd
import json, re

with open('re_loudong.txt', mode='r') as file:
    re_loudong = json.loads(file.read())

xlsx = pd.read_excel('小资家allnew.xlsx')
xiaozijia_district = {}
for x in xlsx.index:
    data = dict(xlsx.loc[x])
    data_key = str(data['ConstructionId'])
    if data_key not in xiaozijia_district:
        xiaozijia_district[data_key] = data

client = MongoClient('mongodb://goojia:goojia7102@192.168.0.235:27777')
xiaozijia_house_detail_2018_10_8 = client['friends']['xiaozijia_house_detail_2018_10_8']
xiaozijia_detail = client['friends']['xiaozijia_detail']

def get_format_loudong(loudong):
    re_num = re.sub(r'[0-9]', '0', loudong)
    re_num = re.sub(r'[a-zA-Z]', 'x', re_num)
    for k, v in {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'}.items():
        loudong = loudong.replace(k, v)
    if re_num in re_loudong:
        match1 = re.match(r'{}'.format(re_loudong[re_num]), loudong)
        if match1:
            return match1.group(1)


if __name__ == '__main__':
    house = {}
    n = 0
    for i in xiaozijia_house_detail_2018_10_8.find({},
                                                   {'ConstructionId': 1, 'BuildingId': 1, 'HouseOrientation': 1,
                                                    'HouseName': 1, '_id': 1}).limit(7000):
        if i['BuildingId'] not in house:
            house[i['BuildingId']] = i['HouseOrientation']

            buildName = xiaozijia_detail.find_one({'BuildingId':i['BuildingId']},{'BuildName':1})
            if buildName and 'BuildName' in buildName and buildName['BuildName'] not in ['',None]:
                format_loudong = get_format_loudong(buildName['BuildName'])
                if format_loudong:
                    district_info = xiaozijia_district.get(i['ConstructionId'], None)
                    if district_info:
                        Direction.update_direction(district_info['city'], district_info['region'],
                                                   district_info['ConstructionName'], format_loudong, i['HouseOrientation'], '小资家')


