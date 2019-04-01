from pymongo import MongoClient
import requests, json, re

class CutAddress:

    precise_address = '.*[镇区县市海】](.+(路|街|大道|巷|道|((一|二|三|四|五|六|七|八|九|十|东|南|西|北|复)' \
                      '[线环条甲])|(胡同))(交汇|.{0,3}段|.*弄)?((([一二三四五六七八九十百千\d])+弄)|([甲乙]?' \
                      '([一二三四五六七八九十百千\d]))+号(?!楼)))'

    @classmethod
    def re_address(cls, auction_name):
        if '号' in auction_name:
            cut_add = re.match(r'.*[村镇区县市海】](.*?(路|街|巷|道|线|弄|胡同)\d+?号)', auction_name)
        else:
            cut_add = re.match(r'.*[村镇区县市海】](.*(弄|路|街|巷|道|线|胡同))', auction_name)

        if cut_add and len(cut_add.group(1)) in range(3, 15):
            return cut_add.group(1)
        else:
            cut_add = re.match(r'{}'.format(cls.precise_address),auction_name)
            if cut_add and len(cut_add.group(1)) in range(3, 15):
                return cut_add.group(1)

class CutRegion:

    client = MongoClient('192.168.0.136', 27017)
    region_block = client['fangjia']['region_block']
    region_list = list(region_block.find({'category': 'region'},
                                         {'city': 1, 'name': 1, 'pattern': 1, '_id': 0}))

    @classmethod
    def get_region(cls, city, name):
        for r in cls.region_list:
            if city in r['city']:
                for p in r['pattern']:
                    if p in name:
                        return r['name']

class CutHousenum:

    @classmethod
    def re_housenum(self, auction_name):
        house_list = ['.*([1-9a-zA-Z]+)(幢|栋|座|号楼)',
                      '.*小区(.*)号',
                      '.*[村弄庭]([1-9a-zA-Z]+)号',
                      '.*弄(.*)号']
        for p in house_list:
            num = re.match(r'{}'.format(p), str(auction_name))
            if num:
                if p == '.*弄(.*)号':
                    if '、' in num.group(1) or '.' in num.group(1):
                        newnum = num.group(1).replace('、',';').replace('.',';').split('号')[0]
                        return newnum
                    else:
                        return None
                return num.group(1)

class CutRoomnum:

    @classmethod
    def re_roomnum(self, auction_name):
        room_list = ['[楼幢栋座层号](.*)[室房]',
                     '[楼|幢|栋|座]([0-9a-zA-Z]+)层?!',
                     '([0-9a-zA-Z]+)[室房]',
                     '层([0-9a-zA-Z])号']
        for p in room_list:
            num = re.findall(r'{}'.format(p), str(auction_name))
            if len(num) > 0:
                if p == '[楼幢栋座层号](.*)[室房]':
                    for k in ['楼','幢','栋','座','层']:
                        if k in num[0]:
                            num[0] = num[0].split(k)[1]
                    inum = re.findall(r'([0-9a-zA-Z]+)', num[0])
                    for n in inum:
                        if len(n) < 2:
                            inum.remove(n)
                    return ';'.join(inum)
                if len(num[0]) < 6:
                    return ';'.join(num)

class CutMatch(CutRegion, CutAddress, CutHousenum, CutRoomnum):

    @classmethod
    def getLocation(cls, city, name):
        mapLng, mapLat = None, None
        url = 'https://restapi.amap.com/v3/geocode/geo?'
        pay_load = {'key': '3f0288dd640f0ba8308d1f31384e4ef9', 'city': city, 'address': name, 'output': 'json'}
        r = requests.get(url, params=pay_load)
        text = json.loads(r.content, encoding='utf-8')
        if text['status'] == '1' and text['info'] == 'OK':
            try:
                mapLng, mapLat = text['geocodes'][0]['location'].split(',')
            except:
                pass
        return mapLng, mapLat

    @staticmethod
    def judge_cut(name, cutlist):
        for c in cutlist:
            if c in name:
                return c

    @staticmethod
    def format_name(auction_name):

        rk_list = re.findall(r'(【.*】)', auction_name)
        if len(rk_list) > 0:
            for rk in rk_list:
                auction_name = auction_name.replace(rk, '')

        for k in ['(',')','（','）']:
            auction_name = auction_name.replace(k, '')

        for a in auction_name:

            chs_arabic_map = {'０': '0', '１': '1', '２': '2','３': '3', '４': '4','５': '5', '６': '6',
                              '７': '7', '８': '8', '９': '9','位于': '', ' ': '','坐落于': '' }
            try:
                auction_name = auction_name.replace(a, chs_arabic_map[a])
            except:
                pass

        return auction_name

    @classmethod
    def matchApi(cls, keyword, city=None, preciselevel=None, category=None):
        '''
        :param preciselevel: 价格等级：strict
        :param category: 类型：property(小区)
        '''
        key = 'F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD' \
              '286BA38E05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD80046' \
              '0D100D6B667A4ED8EE67C8F7FB'
        url = 'http://open.fangjia.com/address/match?'
        pay_load = {'address': keyword, 'city': city, 'preciseLevel': preciselevel, 'category': category,
                    'token': key}
        r = requests.get(url, params=pay_load)
        text = json.loads(r.content, encoding='utf-8')
        if text['msg'] == 'ok':
            return text['result']

    @classmethod
    def get_name_list(cls, fj_match):
        name_list = []
        try:
            name_list.append(fj_match['name'])
        except:
            pass
        try:
            name_list.append(fj_match['suggestName'])
        except:
            pass
        try:
            for name in fj_match['alias']:
                name_list.append(name)
        except:
            pass

        return name_list

    @classmethod
    def get_addr_list(cls, fj_match):
        add_list = []
        try:
            add_list.append(fj_match['address'])
        except:
            pass
        try:
            add_list.append(fj_match['suggestAddress'])
        except:
            pass
        try:
            for add in fj_match['addr_alias']:
                add_list.append(add)
        except:
            pass
        try:
            add_list.append(fj_match['searchAddress']['street'] + fj_match['searchAddress']['streetNumber'])
        except:
            try:
                add_list.append(fj_match['searchAddress']['street'])
            except:
                pass
        if len(add_list) > 0:
            return add_list

    @classmethod
    def to_match(cls, city, auction_name):

        new_name = cls.format_name(auction_name)

        fj_match = cls.matchApi(new_name, city=city)

        matchCity, matchRegion, matchName, matchAddress = list(None for i in range(4))

        name_list, addr_list = ([], [])

        if fj_match:

            name_list = cls.get_name_list(fj_match)

            addr_list = cls.get_addr_list(fj_match)

            if fj_match['credit'] > 0:
                name_address = name_list + addr_list if len(addr_list) > 2 else name_list
                matchName = fj_match['name'] if cls.judge_cut(new_name, name_address) else None
                if matchName:
                    matchCity, matchRegion, matchName, matchAddress = fj_match['city'], fj_match['district'], fj_match['name'], fj_match['address']

        cutCity = cls.judge_cut(new_name, [city, '上海'])

        cutRegion = cls.get_region('上海', new_name)

        cutName = cls.judge_cut(new_name, name_list)

        ad = cls.re_address(new_name)
        cutAddress = ad if ad else cls.judge_cut(new_name, addr_list)

        cutHousenum = cls.re_housenum(new_name)
        if not cutHousenum:
            try:
                cutHousenum = fj_match['buildingNumber']
            except:
                pass

        cutRoomnum = cls.re_roomnum(new_name)
        if not cutRoomnum:
            try:
                cutHousenum = fj_match['roomNumber']
            except:
                cutHousenum = None

        data_dict = {}

        data_dict['mapLng'], data_dict['mapLat'] = cls.getLocation(city, new_name)

        data_dict['cutCity'], data_dict['cutRegion'], data_dict['cutName'], data_dict['cutAddress'] = cutCity, cutRegion, cutName, cutAddress
        data_dict['cutHousenum'], data_dict['cutRoomnum'] = cutHousenum, cutRoomnum
        data_dict['matchCity'], data_dict['matchRegion'], data_dict['matchName'], data_dict['matchAddress'] = matchCity, matchRegion, matchName, matchAddress
        return data_dict

