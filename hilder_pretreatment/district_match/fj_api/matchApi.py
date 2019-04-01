import requests, json

key = "F54F52381C49BB9EB4A33EB1B65604AE4B71A28AEE53518A94A2F360408B9056D57553931D15CE6DDE765562DAD286BA38E" \
      "05A4CDAFC51C3D527A4959BF8E75A3B95DB7108FCEA340DDE61925616DB55118E1851E67D83EAD800460D100D6B667A4ED8EE67C8F7FB"


def match_api(keyword, city=None, preciselevel=None, category=None):
    """
    :param keyword:
    :param city
    :param preciselevel: 价格等级：strict
    :param category: 类型：property

    :return
    """
    url = 'http://open.fangjia.com/address/match?'
    pay_load = {'address': keyword, 'city': city, 'preciseLevel': preciselevel, 'category': category, 'token': key}
    r = requests.get(url, params=pay_load)
    if r.json()['msg'] == 'ok':
        return r.json()['result']
