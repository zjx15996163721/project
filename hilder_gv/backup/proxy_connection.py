import requests
import random
from lib.log import LogHandler
import json

log = LogHandler('proxy')

class Proxy_contact():
    def __init__(self,app_name=None,method=None,url=None,ban_word=None,formdata=None,session=None,headers=None):
        self.app_name = app_name
        self.method = method
        self.url = url
        self.ban_word = ban_word
        self.formdata = formdata
        self.session = session
        self.headers = headers   #支持自定义headers

    def contact(self):
        try:
            if self.method == 'get':  #get请求
                count = 0
                while True:
                    proxy_ip = self.get_proxy()
                    proxies = {"http": "http://" + proxy_ip}
                    try:
                        res = requests.get(self.url,proxies=proxies,headers=self.headers,timeout=10,)
                        if res.status_code == 200:
                            # if self.ban_word in res.content.decode(self.encode):
                            #     self.post_back(proxy_ip, 1)
                            self.post_back(proxy_ip, 0)
                            break
                        else:
                            count += 1
                            continue
                    except:
                        self.post_back(proxy_ip, 1)
                        count += 1
                        # log.debug("尝试第{}次重新连接".format(count))
                        if count >= 200:
                            # log.error('重连失败！')
                            print("重连失败")
                            return False
                        print("尝试第{}次重新连接".format(count))
                        continue
                return res.content

            elif self.method == 'post':         #post请求(json格式返回) session保持会话
                count = 0
                while True:
                    proxy_ip = self.get_proxy()
                    proxies = {"http": ("http://" + proxy_ip)}
                    try:
                        res = self.session.post(self.url,data=self.formdata,proxies=proxies,headers=self.headers,timeout=10)
                        if res.status_code == 200:
                            con_dict = json.loads(res.text)
                            self.post_back(proxy_ip, 0)
                            break
                        elif count == 200:
                            log.error('重连失败！')
                            break
                        else:
                            continue
                    except:
                        self.post_back(proxy_ip,1)
                        count += 1
                        log.info("尝试第{}次重新连接".format(count))
                        continue
                return con_dict
            else:
                log.error("method wrong！")
        except Exception as e:
            log.error(e)


    def get_proxy(self):
        api_1 = "http://192.168.0.191:8999/get_one_proxy"
        app_name = self.app_name
        data = {"app_name":app_name,}
        try:
            proxy_ip = requests.post(api_1, data=data).text
            return proxy_ip
        except Exception as e:
            log.error(e)

    def post_back(self,ip,code):
        api_2="http://192.168.0.191:8999/send_proxy_status"
        data = {
            "app_name":self.app_name,
            "ip":ip,
            "status_code":code,
        }
        try:
            requests.post(api_2, data=data)
        except Exception as e:
            log.error(e)

