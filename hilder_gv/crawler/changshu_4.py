"""
url = http://www.jscsfc.com/NewHouse/
city: 常熟
CO_INDEX: 4

"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import requests, re
from lxml import etree

co_index = "4"
city = '常熟'

count = 0


class Changshu(Crawler):
    def __init__(self):
        self.url = 'http://www.jscsfc.com/NewHouse/'

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
            'Referer': 'http://www.jscsfc.com/NewHouse/',
            # 'Cookie':'UM_distinctid=162292d7c2963c-0327a1123131c1-444a012d-1fa400-162292d7c2a2d6; CNZZDATA2499568=cnzz_eid%3D1244283227-1521108356-%26ntime%3D1521180043'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='ount">(\d+)</span></b>页',
                       )
        page = b.get_page_count()
        list_formdata = {}
        for i in range(1, int(page) + 1):

            response = requests.post(self.url, data=list_formdata, headers=self.headers)
            con = etree.HTML(response.text)

            href_list = con.xpath("//strong/a/@href")
            view_state = con.xpath("//input[@id='__VIEWSTATE']/@value")[0]
            valid = con.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
            list_formdata["__VIEWSTATE"] = view_state  # 保存当前页的信息作为下一页请求参数
            list_formdata["__EVENTVALIDATION"] = valid
            list_formdata["ctl00$ContentPlaceHolder1$PageNavigator_NewHouse1$txtNewPageIndex"] = i
            list_formdata["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$PageNavigator_NewHouse1$LnkBtnGoto"

            for href in href_list:
                new_url = self.url + href

                res = requests.get(new_url, headers=self.headers)
                comm_con = res.text

                detail_url = re.search('楼盘明细：.*?"(.*?)"', comm_con).group(1)
                detail_url = self.url + detail_url
                response = requests.get(detail_url)
                html = etree.HTML(response.text)
                comm_url_list = html.xpath("//div[@class='Search_results_box']//td/a/@href")

                for comm_url in comm_url_list:
                    commurl = self.url + comm_url
                    comm_res = requests.get(commurl, headers=self.headers)
                    comm_con = comm_res.text
                    bo_develops = re.search('开发企业.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                    if bo_develops is None:
                        continue
                    else:
                        try:
                            co = Comm(co_index)
                            co.co_name = re.search('<h1>(.*?)<span>', comm_con, re.S | re.M).group(1)
                            co.co_develops = bo_develops
                            co.co_id = re.search('MID=(\d+)', comm_url).group(1)
                            co.co_use = re.search('规划用途.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_address = re.search('项目坐落.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_build_start_time = re.search('开工时间.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_build_end_time = re.search('竣工时间.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_size = re.search('土地面积.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_build_size = re.search('建筑面积.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.co_all_house = re.findall('#eff6ff">(.*?)</td>', comm_con, re.S | re.M)[0]
                            co.area = re.search('所属区域.*?">(.*?)</td>', comm_con, re.S | re.M).group(1)
                            co.insert_db()
                            global count
                            count += 1
                            print(count)
                            print(co.co_name)
                        except:
                            continue
                        self.build_crawler(co.co_id, co.co_name, comm_con)

    def build_crawler(self, co_id, co_name, comm_con):

        bu = Building(co_index, co_id=co_id, co_name=co_name)
        build_list = re.search('查看楼盘表.*?<tr>(.*?)</table>', comm_con, re.S | re.M).group(1)
        build = re.findall('<tr>(.*?)</tr>', build_list, re.S | re.M)

        for bul in build:
            try:
                bul_html = etree.HTML(bul)
                buli = bul_html.xpath("//td/text()")

                bu.bu_num = bu_num = buli[1]
                bu.bu_all_house = buli[2]
                bu.size = buli[3]
                house_url = re.search(r'"(.*?)" t', bul, ).group(1)
                bu.bu_id = bu_id = re.search('-(\d+)', house_url).group(1)

                bu.insert_db()
            except:
                continue
            self.house_crawler(house_url, bu_num, co_id, bu_id)

    def house_crawler(self, house_url, bu_num, co_id, bu_id):
        ho = House(co_index, bu_num=bu_num, co_id=co_id, bu_id=bu_id)

        url = self.url + house_url
        con = requests.get(url, headers=self.headers)
        tr = con.text
        ho_name = re.findall('室号：(.*?)户', tr, re.S | re.M)  # 房号：3单元403
        # ho_num = re.findall('_td(\d+)"', tr)  # 房号id
        ho_floor = re.findall('(\d+)层', tr)  # 楼层
        ho_type = re.findall('房屋属性：(.*?)"', tr, re.S | re.M)  # 房屋类型：普通住宅 / 车库仓库
        ho_room_type = re.findall('户型：(.*?)所', tr, re.S | re.M)  # 户型
        ho_build_size = re.findall('建筑面积：(.*?)房', tr, re.S | re.M)  # 建筑面积

        for floor in ho_floor:
            try:
                ho.ho_floor = floor
                for index in range(1, len(ho_name) + 1):
                    ho.ho_name = ho_name[index]
                    ho.ho_type = ho_type[index]
                    ho.ho_room_type = ho_room_type[index]
                    ho.ho_build_size = ho_build_size[index]
                    # ho.ho_num = ho_num[index]

                    ho.insert_db()
            except:
                continue


if __name__ == '__main__':
    a = Changshu()
    a.start_crawler()
