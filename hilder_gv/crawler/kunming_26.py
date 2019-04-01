"""
url = http://www.kmhouse.org/moreHousePriceList.asp?page=1
city : 昆明
CO_INDEX : 26
小区数量：1180
"""
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import requests, re
from urllib import parse
from retry import retry

url = 'http://www.kmhouse.org/moreHousePriceList.asp?'
co_index = '26'
city = '昆明'

count = 0


class Kunming(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    @retry(tries=3)
    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='strong>1/(.*?)<',
                       headers=self.headers
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            index_url = 'http://www.kmhouse.org/moreHousePriceList.asp?page=' + str(i)
            try:
                response = requests.get(url=index_url, headers=self.headers)
                html = response.content.decode('gbk')
                comm_url_list = re.findall("cellspacing='3'.*?<a href='(.*?)'", html)
                self.get_comm_info(comm_url_list)
            except Exception as e:
                print('page页错误，co_index={},url={}'.format(co_index, index_url), e)

    @retry(tries=3)
    def get_comm_detail(self, comm_detail_url):
        comm_url = 'http://www.kmhouse.org' + comm_detail_url
        try:
            comm = Comm(co_index)
            response = requests.get(comm_url, headers=self.headers)
            html = response.content.decode('gbk')
            co_id = re.search('Preid=(.*?)&', comm_detail_url).group(1)
            co_name = re.search('楼盘名称.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            area = re.search('所在地区.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            co_address = re.search('楼盘地址.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            co_pre_sale = re.search('预售证号.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            co_volumetric = re.search('容&nbsp;积&nbsp;率.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            co_green = re.search('绿&nbsp;化&nbsp;率.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            co_build_start_time = re.search('开工时间.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
            comm.co_name = co_name
            comm.area = area
            comm.co_id = co_id
            comm.co_address = co_address
            comm.co_pre_sale = co_pre_sale
            comm.co_volumetric = co_volumetric
            comm.co_green = co_green
            comm.co_build_start_time = co_build_start_time
            comm.insert_db()
            global count
            count += 1
            print('count：', count)
        except Exception as e:
            print('小区详情错误，co_index={},url={}'.format(co_index, comm_url), e)

    @retry(tries=3)
    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm_url = "http://www.kmhouse.org" + i
            try:
                co_id = re.search("PreId=(.*?)&", i).group(1)
                s = re.search('prename=(.*?)$', comm_url, re.S | re.M).group(1)
                s_decode_str = parse.quote(s, encoding='gbk')
                comm_url = comm_url.replace(s, s_decode_str)
                response = requests.get(comm_url, headers=self.headers)
                html = response.content.decode('gbk')
                comm_detail_url = re.findall('linkone" href="(.*?)"', html, re.S | re.M)[0]
                self.get_comm_detail(comm_detail_url)
                build_html = re.search('请选择幢号.*?</select>', html, re.S | re.M).group()
                bu_info_list = re.findall("<option.*?</option>", build_html, re.S | re.M)
                for info in bu_info_list:
                    build = Building(co_index)
                    build.bu_id = re.search("value='(.*?)'", info, re.S | re.M).group(1)
                    build.bu_num = re.search("<option.*?>(.*?)<", info, re.S | re.M).group(1)
                    build.co_id = co_id
                    build.insert_db()
                    self.get_build_info(build.bu_id, co_id)
            except Exception as e:
                print('小区错误，co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, bu_id, co_id):
        build_url = 'http://www.kmhouse.org/newhouse/houseprice.asp?PreId=' + co_id + '&Aid=1'
        try:
            data = {
                'bid': bu_id,
                'mess': '1',
                'aid': '1',
                'preid': co_id,
                'issearch': 'yes'
            }
            response = requests.post(build_url, data=data, headers=self.headers)
            html_new = response.content.decode('gbk')
            all_page = re.search('页次:1/(.*?)\n', html_new).group(1)
            self.get_house_url(all_page, co_id, bu_id)
        except Exception as e:
            print('楼栋错误，co_index={},url={}'.format(co_index, build_url), e)

    def get_house_url(self, all_page, co_id, bu_id):
        for i in range(1, int(all_page)):
            house_url = 'http://www.kmhouse.org/newhouse/houseprice.asp?page=' + str(
                i) + '&aid=1&preid=' + co_id + '&bid=' + bu_id + '&issearch=yes'
            try:
                response = requests.get(house_url, headers=self.headers)
                html_house = response.content.decode('gbk')
                info_html = re.search('<table class=warp_table.*?</table>', html_house, re.S | re.M).group()
                info_list = re.findall('<tr height=30>.*?</tr>', info_html, re.S | re.M)
                for info in info_list:
                    house = House(co_index)
                    house.ho_name = re.search('<a.*?><.*?>(.*?)<', info, re.S | re.M).group(1)
                    house.bu_id = bu_id
                    house.co_id = co_id
                    house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, house_url), e)
