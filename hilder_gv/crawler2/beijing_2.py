"""
网站有问题
"""

"""
url: http://www.bjjs.gov.cn/eportal/ui?pageId=307678
city: 北京
CO_INDEX: 2
author: 吕三利
小区数量：4716   2018/2/11
"""
from backup.crawler_base import Crawler
import requests
import re
import math
from backup.comm_info import Comm, Building, House
from retry import retry

count = 0
co_index = 2


class Beijing(Crawler):
    def __init__(self):
        self.url = 'http://www.bjjs.gov.cn/eportal/ui?pageId=307678'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
            'Referer': 'http://www.bjjs.gov.cn/eportal/ui?pageId=307678',
            'Cookie': 'JSESSIONID=A522CA97CD3A946632840E8636A58657; Hm_lvt_9ac0f18d7ef56c69aaf41ca783fcb10c=1518315836,1519631516,1519961932,1519962558; Hm_lpvt_9ac0f18d7ef56c69aaf41ca783fcb10c=1519962569'
        }

    def start_crawler(self):
        self.start()

    @retry(tries=3)
    def get_all_page(self):
        try:
            response = requests.post(url=self.url, headers=self.headers)
            if response.status_code is 200:
                html = response.text
                page_num = re.search('总记录数:(\d+),', html).group(1)
                page = math.ceil(int(page_num) / 15)
                return page
            else:
                pass
        except Exception as e:
            print('page页面错误,co_index={},url={}'.format(co_index, self.url), e)
            raise

    @retry(tries=3)
    def start(self):
        page = self.get_all_page()
        for page in range(1, int(page) + 1):
            params = {'currentPage': page}
            response = requests.post(url=self.url, params=params, headers=self.headers)
            html = response.text.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
            self.get_comm_info(html)

    def get_comm_info(self, html):
        html_info = re.search('预售商品房住宅项目公示(.*?)</table>', html).group(1)
        comm_list = re.findall(
            '<td(.*?)ahref="(.*?)">(.*?)</a(.*?)<ahref="(.*?)">(.*?)</a></td><td(.*?)>(.*?)</td></tr>', html_info)
        for i in comm_list:
            try:
                comm = Comm(2)
                url = 'http://www.bjjs.gov.cn/' + i[1]
                self.get_comm_detail(url, comm)
                global count
                count += 1
                print(count)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, url), e)

    @retry(tries=3)
    def get_comm_detail(self, url, comm):
        response = requests.get(url=url, headers=self.headers)
        comm_html = response.text.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
        co_id = re.search('projectID=(\d+)&', url).group(1)  # 小区id
        co_name = re.search('id="项目名称(.*?)>(.*?)<', comm_html).group(2)  # 小区名称
        co_address = re.search('id="坐落位置(.*?)>(.*?)<', comm_html).group(2)  # 小区地址
        co_pre_sale = re.search('id="预售许可证编号(.*?)>(.*?)<', comm_html).group(2)  # 预售证书
        co_build_size = re.search('id="准许销售面积(.*?)>(.*?)<', comm_html).group(2)  # 建筑面积
        co_develops = re.search('id="开发企业(.*?)>(.*?)<', comm_html).group(2)  # 建筑面积
        co_pre_sale_date = re.search('id="发证日期(.*?)>(.*?)<', comm_html).group(2)  # 发证日期
        comm.co_id = co_id
        comm.co_name = co_name
        comm.co_address = co_address
        comm.co_pre_sale = co_pre_sale
        comm.co_build_size = co_build_size
        comm.co_develops = co_develops
        comm.co_pre_sale_date = co_pre_sale_date
        comm.insert_db()
        # build
        build_info_list = re.findall(
            '--><tr><td(.*?)>(.*?)</td><(.*?)>(.*?)</td><(.*?)>(.*?)</td><(.*?)>(.*?)</td><td(.*?)>(.*?)<',
            comm_html)
        self.get_build_info(build_info_list, co_id, comm_html, url)

    @retry(tries=3)
    def get_build_info(self, build_info_list, co_id, comm_html, url):
        for i in build_info_list:
            try:
                building = Building(2)
                bu_name = i[1]  # 楼栋名称
                bu_num = bu_name.split('#')[0]  # 楼号
                bu_all_house = i[3]  # 总套数
                bu_build_size = i[5]  # 面积
                bu_price = i[9]  # 价格
                # 给对象增加属性
                building.bu_name = bu_name
                building.bu_num = bu_num
                building.bu_all_house = bu_all_house
                building.bu_build_size = bu_build_size
                building.bu_price = bu_price
                building.co_id = co_id  # 小区id
                build_html = re.search(r'楼盘表(.*?)个楼栋信息', comm_html).group(1)
                build_url = re.search(r'<ahref="(.*?)">查看信息<', build_html).group(1)
                build_id = re.search('buildingId=(.*?)$', build_url).group(1)
                building.bu_id = build_id  # 楼栋id
                building.insert_db()
                self.get_build_detail(build_url, co_id)
            except Exception as e:
                print('楼栋错误,co_index={},url={}'.format(co_index, url), e)

    def get_build_detail(self, build_url, co_id):
        url = 'http://www.bjjs.gov.cn' + build_url
        bu_id = re.search(r'buildingId=(.*?)$', build_url).group(1)
        response = requests.get(url, headers=self.headers)
        html = response.text
        house_html = re.search('房 号.*?提示', html, re.S | re.M).group()
        house_html_list = re.findall(r'<div id=.*?</div>', house_html, re.S | re.M)
        for i in house_html_list:
            try:
                house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                ho_name = re.search('<a.*?>(.*?)<', i, re.S | re.M).group(1)
                self.get_house_info(house_url, ho_name, bu_id, co_id)
            except Exception as e:
                print('房号错误,co_index={},url={}'.format(co_index, house_url), e)

    def get_house_info(self, house_url, ho_name, bu_id, co_id):
        house = House(co_index)
        url = 'http://www.bjjs.gov.cn' + house_url
        if '#' not in url:
            house = self.get_house_detail(url, house)
        house.ho_name = ho_name
        house.bu_id = bu_id
        house.co_id = co_id
        house.insert_db()

    def get_house_detail(self, url, house):
        response = requests.get(url, headers=self.headers)
        html = response.text.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
        ho_type = re.search('规划设计用途</td><(.*?)>(.*?)<', html).group(2)  # 房屋类型：普通住宅 / 车库仓库
        ho_room_type = re.search('户　　型</td><(.*?)>(.*?)<', html).group(2)  # 户型：一室一厅
        ho_build_size = re.search('>建筑面积</td><(.*?)>(.*?)平方米<', html).group(2)  # 建筑面积
        ho_true_size = re.search('>套内面积</td><(.*?)>(.*?)平方米<', html).group(2)  # 预测套内面积,实际面积
        ho_price = re.search('>按建筑面积拟售单价</td><(.*?)>(.*?)元/平方米<', html).group(2)  # 价格
        ho_share_size = float(ho_build_size) - float(ho_true_size)  # 分摊面积
        house.ho_type = ho_type
        house.ho_room_type = ho_room_type
        house.ho_build_size = ho_build_size
        house.ho_true_size = ho_true_size
        house.ho_price = ho_price
        house.ho_share_size = ho_share_size
        return house


if __name__ == '__main__':
    b = Beijing()
    b.start_crawler()
