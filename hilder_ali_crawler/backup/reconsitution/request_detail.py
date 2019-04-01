import re, requests
import random
import uuid
from dianping.rk import RClient
from fake_useragent import UserAgent
from selenium import webdriver
import time

ua = UserAgent()
s = requests.session()
rc = RClient('ruokuaimiyao', '205290mima', '95632', '6b8205cf61944329a5841c30e5ed0d5d')


def get_cookie():
    browser = webdriver.ChromeOptions()
    browser.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=browser, executable_path='../chromedriver.exe')
    browser.get("http://www.dianping.com/")
    coo = browser.get_cookies()
    cookie_ = ''
    for i in coo:
        name = i['name']
        value = i['value']
        c = name + '=' + value + ';'
        cookie_ += c
    browser.close()
    return cookie_


# cookie_ = 'cy=8; cye=chengdu; _lxsdk_cuid=1642070d693c8-0a5d980b8e9bc8-39614101-1aeaa0-1642070d695c8; _lxsdk=1642070d693c8-0a5d980b8e9bc8-39614101-1aeaa0-1642070d695c8; _hc.v=cf54ce12-f9da-1ebf-5fd1-a408310e7965.1529552623; s_ViewType=10; _lxsdk_s=1642070d696-5b3-eef-2a7%7C%7C22'
cookie_ = 's_ViewType=10; _lxsdk_cuid=164207c9779c8-05327cde9d5a2f-39614101-1aeaa0-164207c97799d; _lxsdk=164207c9779c8-05327cde9d5a2f-39614101-1aeaa0-164207c97799d; _hc.v=85a493b1-df06-3363-7751-85cce8f9bd7f.1529553394; _lxsdk_s=164207c977b-a15-397-b64%7C%7C37'
# cookie_ = 'cy=8; cye=chengdu; _lxsdk_cuid=164207ecb2cc8-0e10df803ec6-39614101-1aeaa0-164207ecb2cc8; _lxsdk=164207ecb2cc8-0e10df803ec6-39614101-1aeaa0-164207ecb2cc8; _hc.v=d0651cd4-c617-6643-298c-b4da9ea9ecc6.1529553538; s_ViewType=10; _lxsdk_s=164207ecb2e-bd6-713-7d%7C%7C44'


headers = {
    'User-Agent': ua.random,
    # 'Cookie': get_cookie(),
    'Cookie': cookie_,
}


def request_get(url, ip, connection=None):
    try:
        proxies = {
            'http': ip,
            'https': ip,
        }
        response = requests.get(url, proxies=proxies, headers=headers, timeout=20)
        # connection.process_data_events()
        if 'name="Description"' in response.text:
            print(ip, '¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿')
            return response
        elif '错误信息：请求错误' in response.text:
            print('url无效，url={}'.format(url))
            return 'un_url'
        elif '验证中心' in response.text:
            response = login_dianping(response.text, ip, url, connection)
            if response:
                print('验证成功')
                return response
            else:
                return False
        else:
            print('cookie过期')
            headers['Cookie'] = get_cookie()
            return False

    except Exception as e:
        print(e)
        return None


def login_dianping(html, ip, url, connection):
    requestCode = re.search('requestCode: "(.*?)"', html, re.S | re.M).group(1)
    _token = str(random.randint(1, 100000))
    randomId = str(random.random())
    action = 'spiderindefence'
    url_img = 'https://verify.meituan.com/v2/captcha?' + 'request_code=' + requestCode + '&action=' + action + '&randomId=' + randomId + '&_token' + _token
    proxy = {
        'http': ip,
        'https': ip
    }
    while True:
        print('开始验证', ip)
        res = requests.get(url_img, proxies=proxy, headers=headers, timeout=20)
        # connection.process_data_events()
        html_img = res.content
        img_result_res = rc.rk_create(html_img, 3040)
        if 'Result' not in img_result_res:
            print('快豆不足')
            continue
        img_result = img_result_res['Result']
        uuid_name = str(uuid.uuid1())
        if html_img:
            with open('images/%s_%s.jpg' % (img_result, uuid_name), 'wb') as f:
                f.write(html_img)
        data = {
            'id': '71',
            'request_code': requestCode,
            'captchacode': img_result,
            '_token': _token
        }
        v_url = 'https://verify.meituan.com/v2/ext_api/spiderindefence/verify?id=1'
        time.sleep(0.2)
        response = requests.post(v_url, data=data, headers=headers, proxies=proxy, timeout=20)
        # connection.process_data_events()
        if '请求异常,拒绝操作' in response.text:
            v_url = 'https://verify.meituan.com/v2/ext_api/spiderindefence/verify?id=1'
            time.sleep(0.2)
            response = requests.post(v_url, data=data, headers=headers, proxies=proxy, timeout=10)
            # connection.process_data_events()
            if '请求异常,拒绝操作' in response.text:
                return None
        if 'response_code' not in response.text:
            continue
        response_code = response.json()['data']['response_code']
        print(response_code)
        end_url = 'https://optimus-mtsi.meituan.com/optimus/verifyResult?originUrl=' + url + '&response_code=' + response_code + '&request_code=' + requestCode
        time.sleep(0.2)
        end_res = requests.get(end_url, proxies=proxy, headers=headers, timeout=30)
        # connection.process_data_events()
        if 'name="Description"' in end_res.text:
            with open('images_right/%s_%s.jpg' % (img_result, uuid_name), 'wb') as f:
                f.write(html_img)
            return end_res
        else:
            headers['Cookie'] = get_cookie()
