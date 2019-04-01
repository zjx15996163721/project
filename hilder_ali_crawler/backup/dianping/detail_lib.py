from dianping.request_detail import request_get


def start_detail():
    for i in range(1000000000):
        url = 'http://www.dianping.com/shop/' + str(i)
        ip = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": "http-pro.abuyun.com", "port": "9010",
                                                             "user": "HRH476Q4A852N90P", "pass": "05BED1D0AF7F0715"}
        try:
            response = request_get(url, ip)
            if response == 'un_url':
                continue
            html = response.text
            print(html)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    start_detail()
