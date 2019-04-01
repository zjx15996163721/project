"""
url = http://www.jjzzfdc.com.cn/WebClient/ClientService/frmYsxk_more.aspx?qcount=10000&pcount=33
city : 九江
CO_INDEX : 25

"""
from backup.crawler_base import Crawler
from backup.comm_info import Building, House
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl
import requests, re

url = 'http://www.jjzzfdc.com.cn/WebClient/ClientService/frmYsxk_more.aspx?qcount=10000&pcount=33'
co_index = '25'
city = '九江'


class Jiujiang(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer': 'http://www.jjzzfdc.com.cn/WebClient/ClientService/frmYsxk_more.aspx?qcount=10000&pcount=33'

        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='共(.*?)页',
                       )
        page = b.get_page_count()

        for i in range(1, int(page) + 1):
            all_page_url = url + '&Page=' + str(i)
            p = ProducerListUrl(page_url=all_page_url,
                                request_type='get', encode='gbk',
                                analyzer_rules_dict=None,
                                current_url_rule="eval\('openBldg\((.*?)\)",
                                analyzer_type='regex',
                                headers=self.headers)
            comm_url_list = p.get_current_page_url()
            self.get_build_info(comm_url_list)

    def get_build_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                sid = re.findall('\+(\d+)\+', i)[0]
                pid = re.findall('\+(\d+)\+', i)[1]
                build_url = 'http://www.jjzzfdc.com.cn/WebClient/ClientService/bldg_query.aspx?pid=' + pid + '&sid=' + sid
                # print(build_url)
                response = requests.get(build_url)
                html = response.text
                build = Building(co_index)
                build.bu_id = pid
                build.bu_num = re.search('楼栋座落.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_address = re.search('楼栋座落.*?<td.*?>(.*?)<', html, re.S | re.M).group(1)
                build.bu_pre_sale = re.search('预售证号.*?">(.*?)&nbsp', html, re.S | re.M).group(1)
                build.bu_pre_sale_date = re.search('时间.*?">(.*?)&nbsp', html, re.S | re.M).group(1)
                build.bu_all_house = re.search('dM.*?">(.*?)&nbsp', html, re.S | re.M).group(1)
                # build.bu_address = re.search('售楼处地址.*?">(.*?)&nbsp', html, re.S | re.M).group(1)
                build.insert_db()
            except Exception as e:
                print('co_index={}, 楼栋错误,url={}'.format(co_index, build_url), e)

            house_url = 'http://www.jjzzfdc.com.cn/WebClient/ClientService/proxp.aspx?key=WWW_LPB_001&params=' + sid
            # print(house_url)
            result = requests.get(house_url)
            html_ = result.text

            for house_info in re.findall('<Result.*?</Result>', html_, re.S | re.M):
                try:
                    house = House(co_index)
                    house.bu_id = build.bu_id
                    house.bu_num = build.bu_num
                    house.ho_name = re.search('<ONAME>(.*?)</ONAME>', house_info, re.S | re.M).group(1)
                    house.ho_num = re.search('<OSEQ>(.*?)</OSEQ>', house_info, re.S | re.M).group(1)
                    house.ho_build_size = re.search('<BAREA>(.*?)</BAREA>', house_info, re.S | re.M).group(1)
                    house.ho_floor = re.search('<FORC>(.*?)</FORC>', house_info, re.S | re.M).group(1)
                    house.ho_true_size = re.search('<PAREA>(.*?)</PAREA>', house_info, re.S | re.M).group(1)
                    house.insert_db()
                except Exception as e:
                    print('co_index={}, 房号错误'.format(co_index), e)
