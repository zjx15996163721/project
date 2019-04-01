from backup.crawler_base import Crawler
import requests
from backup.comm_info import Comm, Building, House
import re


class Taian(Crawler):
    def __init__(self):
        self.url_now = 'https://cucc.tazzfdc.com/reisPub/pub/saleBuildingStatist'  # 现售
        self.url_now_source = 'https://cucc.tazzfdc.com/reisPub/pub/saleBuildingStatist'

        self.url_future = 'https://cucc.tazzfdc.com/reisPub/pub/preSaleBuildingStatist'  # 预售
        self.url_future_source = 'https://cucc.tazzfdc.com/reisPub/pub/preSaleBuildingStatist'

        self.house_url = 'https://cucc.tazzfdc.com'

        self.co_index = 50
        self.headers = {
            'Cookie': 'JSESSIONID=027564E74D737A71A8DA9C12F9CE9DAD-n2; pubDistrict=370900'
        }

    def start_crawler(self):
        now_page_count = self.get_count(self.url_now)
        future_page_count = self.get_count(self.url_future)

        print(now_page_count)
        all_now_list_url = self.get_all_comm_info(self.url_now_source, now_page_count,
                                                  'https://cucc.tazzfdc.com/reisPub/pub/saleProjectInfo?')
        all_future_list_url = self.get_all_comm_info(self.url_future_source, future_page_count,
                                                     'https://cucc.tazzfdc.com/reisPub/pub/projectInfo?')

        self.get_build_url(all_now_list_url + all_future_list_url)

    def get_build_url(self, all_list_url):
        # 存储小区的信息，存储楼栋的信息
        for i in all_list_url:
            try:
                res = requests.get(url=i['url'], )
                html_str = res.content.decode()
                c = Comm(self.co_index)
                c.area = i['area']
                c.co_name = re.search('项目名称：.*?left">(.*?)</td>', html_str, re.S | re.M).group(1)
                c.co_owner = re.search('所有权证号：.*?left">(.*?)</td>', html_str, re.S | re.M).group(1)
                c.co_land_use = re.search('土地使用权证：.*?left">(.*?)</td>', html_str, re.S | re.M).group(1)
                c.co_land_type = re.search('土地权证类型：.*?left">(.*?)</td>', html_str, re.S | re.M).group(1)
                print(c.co_name)
                c.insert_db()

                # 找到楼栋
                build_str = re.search('楼盘表<(.*?)/table>', html_str, re.S | re.M).group(1)
                # 遍历所有楼栋
                for k in re.findall('<tr>.*?</tr>', build_str, re.S | re.M):
                    try:
                        b = Building(self.co_index)
                        b.co_name = re.search('项目名称：.*?left">(.*?)</td>', html_str, re.S | re.M).group(1)
                        b.bu_num = re.search('buildingInfo.*?">(.*?)</a>', k, re.S | re.M).group(1)
                        b.bu_build_size = re.findall('<td.*?>(.*?)</td>', k, re.S | re.M)[3]
                        house_url = re.search("this,'(.*?)'\);", k, re.S | re.M).group(1)
                        b.insert_db()

                        complete_url = self.house_url + house_url

                        res = requests.get(url=complete_url, headers=self.headers)
                        # 房号页面
                        house_html_str = res.content.decode()
                        # 找到所有的房号
                        for j in re.findall('a href="(.*?)" target', house_html_str, re.S | re.M):
                            try:
                                h = House(self.co_index)
                                h.bu_num = re.search('<h3 class="h3">(.*?)</h3>', house_html_str, re.S | re.M).group(1)
                                com_url = self.house_url + j
                                res = requests.get(url=com_url, headers=self.headers)
                                house_detail_html = res.content.decode()
                                h.co_name = re.search('项目名称：.*?<td>(.*?)</td>', house_detail_html, re.S | re.M).group(1)
                                h.ho_name = re.search('房　　号：.*?<td>(.*?)</td>', house_detail_html, re.S | re.M).group(1)
                                h.ho_build_size = re.search('建筑面积：.*?<td>(.*?)</td>', house_detail_html,
                                                            re.S | re.M).group(1)
                                h.ho_type = re.search('房屋用途：.*?<td>(.*?)</td>', house_detail_html, re.S | re.M).group(1)
                                h.ho_floor = re.search('所 在 层：.*?<td>(.*?)</td>', house_detail_html, re.S | re.M).group(
                                    1)
                                h.ho_share_size = re.search('分摊面积：.*?<td>(.*?)</td>', house_detail_html,
                                                            re.S | re.M).group(1)
                                h.ho_room_type = re.search('房屋户型：.*?<td>(.*?)</td>', house_detail_html,
                                                           re.S | re.M).group(1)
                                h.ho_true_size = re.search('套内面积：.*?<td>(.*?)</td>', house_detail_html,
                                                           re.S | re.M).group(1)
                                h.insert_db()
                            except Exception as e:
                                print('房号错误，co_index={},url={}'.format(self.co_index, com_url), e)
                                continue
                    except Exception as e:
                        print('楼栋错误，co_index={},url={}'.format(self.co_index, i['url']), e)
                        continue
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(self.co_index, i['url']), e)
                continue

    def get_all_comm_info(self, url, now_page_count, mosaic):
        url_list = []
        for i in range(1, int(now_page_count) + 1):
            try:
                data = {
                    'pageNo': i
                }
                res = requests.post(url=url, data=data, headers=self.headers)
                html_str = res.content.decode()
                page_url_list = []
                for k in re.findall('<tr onmouseover.*?</tr>', html_str, re.S | re.M):
                    try:
                        area = re.search('<div.*?>(.*?)</div>', k, re.S | re.M).group(1)
                        href = re.findall("projectInfo\('(.*?)','(.*?)'\)", k, re.S | re.M)
                        url_ = mosaic + 'id=' + href[0][0] + '&cid=' + href[0][1]
                        area_url_dict = {
                            'area': area,
                            'url': url_
                        }
                        page_url_list.append(area_url_dict)
                    except Exception as e:
                        continue
                url_list = page_url_list + url_list
            except Exception as e:
                continue
        return url_list

    def get_count(self, url):
        res = requests.get(url, headers=self.headers)
        splited_str = re.search('上一页.*?下一页', res.content.decode(), re.S | re.M).group()
        num_list = re.findall('\d+', splited_str, re.S | re.M)
        return max(num_list)
