import requests
import re
import time


def get_token():
    url = 'http://api.ema666.com/Api/userLogin?uName=muliangshu&pWord=mls8715157&Developer=mMMmg1O%2bH%2bBd0FIZ%2blAc6A%3d%3d'
    response = requests.get(url=url)
    token = response.text
    return token


def get_phone(token):
    while True:
        get_phone_url = 'http://api.ema666.com/Api/userGetPhone?ItemId=36322&token=' + token + '&PhoneType=0'
        result = requests.get(url=get_phone_url)
        if result.text:
            phone = re.search(r'\d+', result.text).group()
            return phone


def get_msg(token, phone):
    count = 0
    while True:
        get_msg_url = 'http://api.ema666.com/Api/userSingleGetMessage?token=' + token + '&itemId=36322&phone=' + phone
        result = requests.get(url=get_msg_url)
        print(result.text)
        if 'False' not in result.text:
            msg = re.search(u'验证码为(.*?)，', result.text).group(1)
            print(msg)
            return msg
        print('zzZ')
        time.sleep(5)
        count += 5
        if count == 30:
            phone = get_phone(token)


def exit(token):
    url = 'http://api.ema666.com/Api/userExit?token=' + token
    requests.get(url=url)


if __name__ == '__main__':
    token = get_token()
    phone = get_phone(token)
    print(phone)
    msg = get_msg(token, phone)
    print(msg)
