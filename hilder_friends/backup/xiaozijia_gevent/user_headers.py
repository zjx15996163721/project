import requests
from retry import retry


@retry(tries=3)
def get_headers(UserAccount):
    try:
        login_url = 'http://www.xiaozijia.cn/User/AjaxLogin'
        data = {
            'UserAccount': UserAccount,  # 0
            # 'UserAccount': '18621579838',  # 1
            # 'UserAccount': '13524949590',  # 2
            # 'UserAccount': '15893020331',  # 3.png
            # 'UserAccount': '18702817448',  # 4
            # 'UserAccount': '15708485010',  # 5
            # 'UserAccount': '15584151171',  # 6
            # 'UserAccount': '17182464250',  # 7
            # 'UserAccount': '17077256481',  # 8
            # 'UserAccount': '18374271608',  # 9
            # 'UserAccount': '17086956174',  # 10
            # 'UserAccount': '17169131342',  # 11
            # 'UserAccount': '15087059511',  # 12
            # 'UserAccount': '17180044837',  # 13
            # 'UserAccount': '17195024821',  # 14
            # 'UserAccount': '17173604285',  # 15
            # 'UserAccount': '17094183915',  # 16
            # 'UserAccount': '17131249854',  # 17
            # 'UserAccount': '18345513497',  # 18
            # 'UserAccount': '13408649193',  # 19
            # 'UserAccount': '17155474615',  # 20
            # 'UserAccount': '17139516794',  # 21
            'AccountType': '0',
            'Password': 'goojia123456',
            'RememberMe': 'false',
            'returnUrl': '',
        }

        s = requests.session()
        response = s.post(login_url, data=data)
        html = response.text
        cookie_list = s.cookies.items()
        cookie_ = ''
        for i in cookie_list:
            key = i[0]
            value = i[1]
            string = key + '=' + value + ';'
            cookie_ += string

        headers = {
            'Cookie': cookie_,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }
        return headers
    except Exception as e:
        raise


if __name__ == '__main__':
    headers = get_headers()
    print(headers)
