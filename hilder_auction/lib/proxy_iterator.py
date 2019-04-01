class Proxies:
    def __init__(self):
        self.account = ["FANGJIAHTT1", "FANGJIAHTT2", "FANGJIAHTT3", "FANGJIAHTT4", "FANGJIAHTT5", "FANGJIAHTT6", ]
        self.index = len(self.account)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            self.index = len(self.account) - 1
        else:
            self.index = self.index - 1
        proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
            "host": "http-proxy-sg2.dobel.cn",
            "port": "9180",
            "account": self.account[self.index],
            "password": "HGhyd7BF",
        }
        proxies = {"https": proxy,
                   "http": proxy}
        return proxies

    def get_one(self, proxies_number=7):
        """
        默认为第七个
        :param proxies_number:
        :return:
        """
        proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
            "host": "http-proxy-sg2.dobel.cn",
            "port": "9180",
            "account": "FANGJIAHTT"+str(proxies_number),
            "password": "HGhyd7BF",
        }
        proxies = {"https": proxy,
                   "http": proxy}
        return proxies

    def get_proxies_list(self):
        proxy_list = []
        for i in self.account:
            proxy = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
                "host": "http-proxy-sg2.dobel.cn",
                "port": "9180",
                "account": i,
                "password": "HGhyd7BF",
            }
            proxies = {"https": proxy,
                       "http": proxy}
            proxy_list.append(proxies)
        return proxy_list


if __name__ == '__main__':
    p = Proxies()
    p = p.get_one(proxies_number=1)
    print(p)