"""
url = http://183.63.60.194:8808/public/web/index
city : 河源
CO_INDEX : 17
author:
小区数量：
"""
import time
from backup.comm_info import Comm, Building, House
import re, requests

url = 'http://183.63.60.194:8808/public/web/index?jgid=FC830662-EA75-427C-9A82-443B91E383CB'
co_index = '17'
city = '河源'
count = 0


class Heyuan(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }
        self.s = requests.session()

    def start_crawler(self):
        info_url = 'http://183.63.60.194:8808/api/GzymApi/GetIndexSearchData?Jgid=FC830662-EA75-427C-9A82-443B91E383CB&PageIndex=1&PageSize=2000&Ysxmmc=&Ysxkzh=&Kfsmc=&Kfxmmc='
        # response = self.request_proxy(info_url)
        response = self.s.get(info_url, headers=self.headers)
        html = response.text
        if '网站防火墙' in html:
            print('\r\n\r\n             网站防火墙\r\n\r\n')
            return
        co_url_list = re.findall('YSXMID":"(.*?)"', html)
        self.get_comm_info(co_url_list)

    def request_proxy(self, url):
        data = {"app_name": 'gv_heyuan'}
        while True:
            ip = requests.post(url='http://192.168.0.235:8999/get_one_proxy', data=data).text
            print(ip)
            proxy = {
                'http': ip
            }
            try:
                res = requests.get(url=url, headers=self.headers, proxies=proxy, timeout=5)
                print(res.status_code)
                if res.status_code == 200:
                    print(res.text)
                    return res
            except Exception as e:
                form_data = {"app_name": 'gv_heyuan', "status_code": 1, "ip": ip}
                requests.post(url='http://192.168.0.235:8999/send_proxy_status', data=form_data)
                print('ip有问题')

    def get_comm_info(self, co_url_list):
        for i in co_url_list:
            comm = Comm(co_index)
            comm_url = 'http://183.63.60.194:8808/public/web/ysxm?ysxmid=' + i
            try:
                time.sleep(1)
                response = self.s.get(comm_url, headers=self.headers)
                html = response.text
                comm.co_id = re.search('ysxmid=(.*?)$', comm_url).group(1)
                comm.co_develops = re.findall('kfsmc.*?<a.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_name = re.findall('PresellName.*?<a.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_address = re.findall('ItemRepose.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_build_size = re.findall('PresellArea.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_all_house = re.findall('djrqtd.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_land_use = re.findall('landinfo.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_type = re.findall('zczjtd.*?>(.*?)<', html, re.S | re.M)[0]
                comm.area = re.findall('FQ.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_pre_sale_date = re.findall('FZDatebegin.*?>(.*?)<', html, re.S | re.M)[0]
                comm.co_pre_sale = re.findall('bookid.*?<a.*?>(.*?)<', html, re.S | re.M)[0]
                comm.insert_db()
                bu_address_list = re.findall('onmouseout.*?center.*?center">(.*?)<', html, re.S | re.M)
                bu_num_list = re.findall('onmouseout.*?center.*?center.*?center">(.*?)<', html, re.S | re.M)
                bu_floor_list = re.findall('onmouseout.*?center.*?center.*?center.*?center">(.*?)<', html, re.S | re.M)
                bu_url_list = re.findall('onmouseout.*?href="(.*?)"', html, re.S | re.M)
                self.get_build_info(bu_address_list, bu_num_list, bu_floor_list, bu_url_list, comm.co_id)
                global count
                count += 1
                print(count)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, bu_address_list, bu_num_list, bu_floor_list, bu_url_list, co_id):
        for i in range(len(bu_url_list)):
            build = Building(co_index)
            build.bu_address = bu_address_list[i]
            build.bu_num = bu_num_list[i]
            build.bu_floor = bu_floor_list[i]
            build.co_id = co_id
            # response = self.request_proxy('http://183.63.60.194:8808/public/web/' + bu_url_list[i])
            time.sleep(1)
            response = self.s.get('http://183.63.60.194:8808/public/web/' + bu_url_list[i], headers=self.headers)
            build.bu_id = re.search('ljzid=(.*?)$', bu_url_list[i]).group(1)
            build.insert_db()
            html = response.text
            house_html = re.search('var _table_html_.*?</script>', html, re.S | re.M).group()
            house_url_list = re.findall('房屋号：<a.*?href="(.*?)"', house_html, re.S | re.M)
            try:
                self.get_house_info(house_url_list, build.bu_id)
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index,
                                                       'http://183.63.60.194:8808/public/web/' + bu_url_list[i]), e)

    def get_house_info(self, house_url_list, bu_id):
        for i in house_url_list:
            house = House(co_index)
            house_url = 'http://183.63.60.194:8808/public/web/' + i
            time.sleep(1)
            response = self.s.get(house_url, headers=self.headers)
            if response.status_code is not 200:
                print('房号错误，co_index={},url={}'.format(co_index, house_url))
                continue
            html = response.text
            house.bu_id = bu_id
            house.ho_name = re.search('HouseNO.*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_true_size = re.search('HouseArea.*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_build_size = re.search('SumBuildArea1.*?>(.*?)<', html, re.S | re.M).group(1)
            house.ho_type = re.search('HouseUse.*?>(.*?)<', html, re.S | re.M).group(1)
            house.orientation = re.search('CHX.*?>(.*?)<', html, re.S | re.M).group(1)
            house.insert_db()


if __name__ == '__main__':
    h = Heyuan()
    h.start_crawler()
