import requests


def login(username, password):
    url_login = "http://fggfinance.yunfangdata.com/WeChat/webservice/doLogin"
    data = {'openid': 'ohWOiuP_gteNNJemGpvDG1axnbBc', 'password': password, 'userName': username}
    headers_login = {
        'Content-Length': "0",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/66.0.3359.117 Safari/537.36",
    }
    response = requests.post(url_login, data=data, headers=headers_login)
    access_token = response.json()['data']['access_token']['access_token']
    token_type = response.json()['data']['access_token']['token_type']
    authorization = token_type + ' ' + access_token
    return authorization


def get_city_info(authorization):
    try:
        headers = {'Authorization': authorization}
        city_url = 'http://fggfinance.yunfangdata.com/WeChat/xiaoQuChaXun/getCurrentCity'
        response = requests.get(city_url, headers=headers)
        if response.json()['success']:
            data = response.json()['data']
            currentCity = data['currentCity']
            currentCityPy = data['currentCityPy']
            return currentCity, currentCityPy
        else:
            get_city_info(authorization)
    except Exception as e:
        get_city_info(authorization)
