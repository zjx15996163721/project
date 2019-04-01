"""
url = http://www.gafdc.cn/newhouse/houselist.aspx?hou=0-0-0-0-0-0-&page=1
city : 广安
CO_INDEX : 12
author: 吕三利
小区数量：14页    2018/3/1\
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl
import requests, re

url = 'http://www.gafdc.cn/newhouse/houselist.aspx?hou=0-0-0-0-0-0-&page=1'
co_index = '12'
city = '广安'

count = 0


class Guangan(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='pg.pageCount = (.*?);',
                       )
        page = b.get_page_count()
        all_url_list = []
        for i in range(1, int(page) + 1):
            all_url = 'http://www.gafdc.cn/newhouse/houselist.aspx?hou=0-0-0-0-0-0-&page=' + str(i)
            comm_url_list = self.get_comm_url(all_url)
            all_url_list += comm_url_list
        # 遍历所有小区url
        for i in all_url_list:
            comm_url = 'http://www.gafdc.cn/newhouse/' + str(i.replace('index', 'base'))
            try:
                self.get_comm_info(comm_url)
            except Exception as e:
                print('小区错误,co_index={},url={}'.format(co_index, comm_url), e)
        all_build_url_list = []
        for i in all_url_list:
            build_url = 'http://www.gafdc.cn/newhouse/' + str(i.replace('index', 'table'))
            house_url_list = self.get_build_info(build_url)
            if house_url_list:
                all_build_url_list += house_url_list
            else:
                print('楼栋错误，此小区没有楼栋，co_index={},url={}'.format(co_index, build_url))
        all_house_url_list = []
        form_data_list = []
        for i in all_build_url_list:
            house_url = 'http://www.gafdc.cn/newhouse/GetBuildTableByAjax.ashx'
            data = {
                'itemRecord': i[0],
                'houseCode': i[1]
            }
            all_house_url_list.append(house_url)
            form_data_list.append(data)
        self.get_house_info(form_data_list)

    def get_house_info(self, form_data_list):
        for data in form_data_list:
            house_url = 'http://www.gafdc.cn/newhouse/GetBuildTableByAjax.ashx'
            try:
                response = requests.post(url=house_url, data=data, headers=self.headers)
                html = response.text
                ho_info_html = re.findall("<td width='95'.*?</td>", html, re.S | re.M)
                bu_id_html = re.search("^.*?overflow-x:auto;", html, re.S | re.M).group()
                bu_id = re.findall("GetData\('.*?','(.*?)'\)", bu_id_html, re.S | re.M)[-1]
                for i in ho_info_html:
                    try:
                        h = House(co_index)
                        h.bu_id = bu_id
                        h.ho_name = re.search('<td.*?>(.*?)<', i, re.S | re.M).group(1)
                        h.ho_type = re.search('物业类别：(.*?) ', i, re.S | re.M).group(1)
                        h.ho_build_size = re.search('建筑面积：(.*?) ', html).group(1)
                        h.insert_db()
                    except Exception as e:
                        print('房屋报错，co_index={},url={}'.format(co_index, house_url), e)
            except Exception as e:
                print('房屋报错，co_index={},url={}'.format(co_index, house_url), e)

    def get_build_info(self, all_build_url_list):
        b = Building(co_index)
        b.co_id = "onclick=GetData\('(.*?)',"
        b.bu_id = "onclick=GetData\('.*?','(.*?)'"
        b.bu_num = "font12yellow-leftA'>.*?</span>套</td><td>.*?</td><td>(.*?)<"
        b.bu_all_house = "font12yellow-leftA'>(.*?)<"
        data_list = b.to_dict()
        p = ProducerListUrl(page_url=all_build_url_list,
                            request_type='get', encode='utf-8',
                            analyzer_rules_dict=data_list,
                            current_url_rule="onclick=GetData\('(.*?)','(.*?)'\)",
                            analyzer_type='regex',
                            headers=self.headers)
        house_url_list = p.get_details()
        return house_url_list

    def get_comm_url(self, all_url_list):
        p = ProducerListUrl(page_url=all_url_list,
                            request_type='get', encode='utf-8',
                            current_url_rule="<a class='anone' href='(.*?)'",
                            analyzer_rules_dict=None,
                            analyzer_type='regex',
                            headers=self.headers)
        comm_url_list = p.get_current_page_url()
        return comm_url_list

    def get_comm_info(self, all_url_list):
        try:
            c = Comm(co_index)
            c.co_name = "class='newtopleft font-k'>(.*?)</li>"
            c.co_id = 'form1" method="post" action="house_base\.aspx\?id=(.*?)"'
            c.co_address = "项目位置：</li><li class='DetaimidR font-f'>(.*?)</li></ul>"
            c.area = "地区/商圈：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_develops = "开发商：</li><li class='DetaimidR font-f'>(.*?)</li>"
            c.co_volumetric = "容积率：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_green = "绿化率：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_all_house = "总户数：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_open_time = "开盘时间：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_land_use = "国土使用证：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_plan_pro = "规划许可证：</li><li class='DetaimidR font-f'>(.*?)<"
            c.co_build_size = "建筑面积：</li><li class='DetaimidR font-f'>(.*?)<"
            data_list = c.to_dict()
            p = ProducerListUrl(page_url=all_url_list,
                                request_type='get', encode='utf-8',
                                analyzer_rules_dict=data_list,
                                analyzer_type='regex',
                                headers=self.headers)
            p.get_details()
            global count
            count += 1
            print(count)
        except Exception as e:
            print('小区错误，co_index={},url={}'.format(co_index, all_url_list), e)
