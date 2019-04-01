"""
判断是否精准匹配
"""
from pymongo import MongoClient
import re
from lib.standardization import StandardCity as sc
import requests

client136 = MongoClient('mongodb://192.168.0.136:27017')
seaweed = client136['fangjia']['seaweed']


def format_name_address(name):
    specific_symbol = [".", "|", "•", "、", ";", "；", ",", "，", "·", " "]
    if name == None:
        return name
    for spe in specific_symbol:
        name = name.replace(spe, '')

    other_words = re.search(r'(\(.*\))', name)
    if other_words:
        name = name.replace(other_words.group(), '')

    return name


def match_api(keyword, city=None, preciselevel=None, category=None):
    """
    :param keyword:
    :param city
    :param preciselevel: 价格等级：strict
    :param category: 类型：property

    :return
    """
    key = "F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E" \
          "05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB"
    url = 'http://open.fangjia.com/address/match?'
    pay_load = {'address': keyword, 'city': city, 'preciseLevel': preciselevel, 'category': category, 'token': key}
    r = requests.get(url, params=pay_load)
    if r.json()['msg'] == 'ok':
        return r.json()['result']


class MatchSeaweed:
    # 获取匹配到的小区的名称、名称别名、精确地址、地址别名以及单独的地址别名、别名
    @classmethod
    def seaweed_name_list(cls, match_info_dict):
        # 定义一个list,初始加入名称
        name_list = [match_info_dict['name']]

        # 加入别名
        alias = match_info_dict.get('alias', None)
        if alias:
            name_list += alias

        # 加入精确地址
        pattern = re.compile(r'\d+(号|弄|支|支弄)')
        if re.search(pattern, match_info_dict.get('address', '')):
            name_list.append(match_info_dict['address'])

        # 加入地址别名
        addalias = cls.get_address_alias(match_info_dict['city'], match_info_dict['district'], match_info_dict['name'],
                                         pattern)
        if addalias:
            name_list += addalias
        return name_list, addalias, alias

    @staticmethod
    def get_address_alias(scity, sregion, sname, pattern):
        one = seaweed.find_one({'city': scity, 'region': sregion, 'name': sname, 'status': 0, 'cat': 'district'},
                               {'addr_alias': 1})
        addr_list = []
        if one and 'addr_alias' in one and one['addr_alias'] not in ['', [], None]:
            # 默认地址别名里面的都是精确地址，但是以防万一
            for a in one['addr_alias']:
                if re.search(pattern, str(a)):
                    addr_list.append(a)
            if len(addr_list) > 0:
                return addr_list

    @classmethod
    def from_match_api(cls, city, name_address, region='', category=None):
        format_name = region + name_address if region and region not in name_address else name_address
        match_info_dict = match_api(format_name_address(format_name), city=city, category=category)

        if match_info_dict and match_info_dict['credit'] > 0:
            # 将名称、名称别名、精确地址、地址别名加入一个匹配列
            name_list, addalias, alias = cls.seaweed_name_list(match_info_dict)

            return_data = {'mcity': match_info_dict['city'],
                           'mregion': match_info_dict['district'],
                           'mname': match_info_dict['name'],
                           'maddress': match_info_dict.get('address'),
                           'malias': alias,
                           'maddralias': addalias,
                           '_id': match_info_dict['id']}

            if city == match_info_dict['city'] and (
                    str(region) in match_info_dict['district'] or match_info_dict['district'] in str(region)):
                if name_address in name_list:
                    return_data['flag'] = '精确匹配'
                elif format_name_address(name_address) in name_list:
                    return_data['flag'] = '精确匹配，加别名'
                else:
                    return_data['flag'] = '模糊匹配'
                return return_data
            else:
                return_data['flag'] = '模糊匹配'
                return return_data


def match(city, **kwargs):
    """

    :param city:
    :param kwargs:
            city: 城市
            region: 区域
            keyword: 名称
            category: property(小区),shop(商铺),office(写字楼)
    :return: 匹配结果
    """

    region = kwargs.get('region')
    standard = sc()
    result, format_city = standard.standard_city(city)

    if result:
        result, region = standard.standard_region(format_city, region)
    else:
        return None

    keyword = kwargs.get('keyword')
    if keyword:
        category = kwargs.get('category')
        match = MatchSeaweed.from_match_api(format_city, keyword, region, category)
        return match


if __name__ == '__main__':
    print(match(city='上海', region='长宁', keyword='新泾6村'))
