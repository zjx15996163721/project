"""
url = 'https://restapi.amap.com/v3/config/district?parameters"
"""


class Amap:
    def __init__(self, province):
        key = ''
        self.url = 'https://restapi.amap.com/v3/config/district?keywords={}&subdistrict=3&key={}'.format(province, key)

    def analyzer(self):
        pass


if __name__ == '__main__':
    province_list = []

    for province in province_list:
        a = Amap(province)
