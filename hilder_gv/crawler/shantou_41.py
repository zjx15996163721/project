from backup.crawler_base import Crawler
import requests
import re
from backup.comm_info import Comm, Building, House

co_index = 41


class Shantou(Crawler):
    def __init__(self):
        self.co_index = 41
        self.url = 'http://www.stfcj.gov.cn/stsite/ProjectList/SelledProject.aspx?Page=1'

    def start_crawler(self):
        page_count = self.get_all_page()
        # print(page_count)
        first_page_url_list = []
        for i in range(1, page_count + 1):
            first_page_url_list.append('http://www.stfcj.gov.cn/stsite/ProjectList/SelledProject.aspx?Page=' + str(i))
        comm_url_list = self.get_comm_url_list(first_page_url_list)
        house_url_list = self.analyzer_comm_url(comm_url_list)
        self.get_house_detail(house_url_list)

    def get_house_detail(self, house_url_list):
        for i in house_url_list:
            res = requests.get(i)
            html = res.content.decode('gbk')
            bu_name = re.search('楼号：.*?HouseNum">(.*?)</span>', html, re.S | re.M).group(1)
            co_name = re.search('项目名称.*?PrjName">(.*?)</span>', html, re.S | re.M).group(1)
            ho_id = re.findall("aspx\?Room=(.*?)'.*?<b>(.*?)</b>", html, re.S | re.M)
            # 房号和房号id对应的字段
            ho_id_dict = {}
            for k in ho_id:
                ho_id_dict[k[0]] = k[1]

            house_info = re.findall("<Room><Cell RoomID='(.*?)'.*?BArea='(.*?)'.*?HouseUse='(.*?)'.*?</Room>",
                                    html,
                                    re.S | re.M)
            for j in house_info:
                try:
                    h = House(self.co_index)
                    h.ho_name = ho_id_dict[j[0]]
                    h.ho_true_size = j[1]
                    h.ho_type = j[2]
                    h.co_name = co_name
                    h.bu_num = bu_name
                    h.insert_db()
                except Exception as e:
                    print('房屋错误，co_index={},url={}'.format(co_index, i), e)
                    continue

    def analyzer_comm_url(self, comm_url_list):
        all_url = []
        for i in comm_url_list:
            try:
                res = requests.get(i)
                html = res.content.decode('gbk')
                c = Comm(self.co_index)
                c.co_name = re.search('项目名称：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 项目名称
                c.co_address = re.search('项目地址：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 项目地址
                c.co_develops = re.search('开发商：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 开发商
                c.co_build_size = re.search('总建筑面积：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 建筑面积
                c.co_land_type = re.search('用地依据：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 土地使用证
                c.co_all_house = re.search('>总套数：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 总套数
                c.area = re.search('所在区域：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 地区 area
                c.co_work_pro = re.search('施工许可证：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(1)  # 施工许可证
                c.co_plan_pro = re.search('建设工程规划许可证：.*?">.*?<span.*?>(.*?)</span>', html, re.S | re.M).group(
                    1)  # 规划许可证
                c.insert_db()

                buildlist = re.findall('onmouseover.*?</TR>', html, re.S | re.M)
                url_list = []
                for k in buildlist:
                    try:
                        b = Building(self.co_index)
                        build_list = re.findall('<TD.*?>(.*?)</TD>', k, re.S | re.M)
                        b.co_name = build_list[1]
                        b.bu_num = build_list[2]
                        b.bu_type = build_list[4]
                        b.insert_db()
                        house_url = re.findall('href="(.*?)"', k, re.S | re.M)
                        for j in house_url:
                            url_list.append('http://www.stfcj.gov.cn/stsite/ProjectList/' + j)
                    except Exception as e:
                        print('楼栋错误，co_index={},url={}'.format(co_index, i), e)
                all_url = all_url + url_list
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, i), e)
        return all_url

    def get_comm_url_list(self, first_page_url_list):
        url_list = []
        for i in first_page_url_list:
            res = requests.get(i)
            html = res.content.decode('gbk')
            all_url = re.findall('(ProjectView.*?)"', html, re.S | re.M)
            true_url = []
            for k in all_url:
                true_url.append('http://www.stfcj.gov.cn/stsite/ProjectList/' + k)
            url_list = true_url + url_list
        return url_list

    def get_all_page(self):
        res = requests.get(self.url)
        html_str = res.content.decode('gbk')
        count_str = re.search('当前页第：.*?共(.*?)页', html_str, re.S | re.M).group(1)
        return int(count_str)
