from backup.crawler_base import Crawler
import requests
import re
from backup.comm_info import Comm, Building, House

count = 0
class Yingtai(Crawler):
    def __init__(self):
        self.url = 'http://www.yingtanfdc.com/website/search/q.html?type=spf&city=&price=&wuye=&stat=&key=%u5173%u952E%u5B57'
        self.url_source = 'http://www.yingtanfdc.com'
        self.co_index = 65

    def start_crawler(self):
        url_list = self.get_all_page()
        self.get_build_url_list(url_list)

    def get_build_url_list(self, url_list):
        for i in url_list:
            try:
                res = requests.get(i)
                html = res.content.decode('gbk')
                for k in re.findall('项目名称.*?</dl>', html, re.S | re.M):
                    try:
                        c = Comm(self.co_index)
                        c.co_name = re.search('html">(.*?)</a>', k, re.S | re.M).group(1)
                        c.co_address = re.search('class="address"(.*?)</dd>', k, re.S | re.M).group(1)
                        c.area = re.search('"city">(.*?)</dd>', k, re.S | re.M).group(1)
                        c.co_develops = re.search('"average">(.*?)</dd>', k, re.S | re.M).group(1)
                        c.insert_db()
                        global count
                        count += 1
                        print(count)

                        url = re.search('a href="(.*?)">', k, re.S | re.M).group(1)
                        complete_url = self.url_source + url
                        res = requests.get(complete_url)
                        html = res.content.decode('gbk')
                        build_info_str = re.search('楼盘表</td>(.*?)合  计', html, re.S | re.M).group(1)
                        for j in re.findall('<tr.*?</tr>', build_info_str, re.S | re.M):
                            try:
                                b = Building(self.co_index)
                                b.co_name = re.search('html">(.*?)</a>', k, re.S | re.M).group(1)
                                b.bu_all_house = re.search('absmiddle"  />(.*?)</a>', j, re.S | re.M).group(1)
                                b.bu_num = re.search('="absmiddle"  />(.*?)</a></strong></', j, re.S | re.M).group(1)
                                b.bu_build_size = re.search('td class="t_c">.*?td class="t_c">(.*?㎡)</td>', j,
                                                            re.S | re.M).group(1)
                                b.insert_db()

                                url = re.search('a href="(.*?)"', j, re.S | re.M).group(1)
                                complete_url = self.url_source + url
                                res = requests.get(complete_url)
                                html = res.content.decode('gbk')
                                # 解析html获取iframe表单的数据
                                house_url = self.url_source + re.search('<iframe.*?"(.*?)"', html, re.S | re.M).group(1)
                                logic_house_url = house_url.replace('Default', 'GetData')
                                logic_house_html = requests.get(url=logic_house_url).content.decode()
                                logic_id = re.search('<LOGICBUILDING_ID>(.*?)<', logic_house_html, re.S | re.M).group(1)
                                final_url = 'http://www.yingtanfdc.com/website/presale/home/HouseTableControl/GetData.aspx?LogicBuilding_ID=' + logic_id
                                final_html = requests.get(url=final_url).content.decode('gbk')
                                for l in re.findall('<ROOM_NUMBER>(.*?)</ROOM_NUMBER>', final_html, re.S | re.M):
                                    try:
                                        h = House(self.co_index)
                                        h.info = final_html
                                        h.ho_name = l
                                        h.co_name = re.search('html">(.*?)</a>', k, re.S | re.M).group(1)
                                        h.bu_num = re.search('="absmiddle"  />(.*?)</a></strong></', j,
                                                             re.S | re.M).group(1)
                                        h.insert_db()
                                    except Exception as e:
                                        continue
                            except Exception as e:
                                continue
                    except Exception as e:
                        continue
            except Exception as e:
                continue

    def get_all_page(self):
        res = requests.get(self.url, )
        html = res.content.decode('gbk')
        url_list = []
        for i in re.findall('href="(/website/search/.*?)"', html, re.S | re.M):
            url_list.append(self.url_source + i)
        url_list.append(self.url)
        return url_list
