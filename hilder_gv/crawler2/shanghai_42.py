from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import requests
import re

co_index = 42


class Shanghai(Crawler):
    def __init__(self):
        self.url = 'http://www.fangdi.com.cn/complexpro.asp'
        self.co_index = 42
        self.area_list = [1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 3, 4, 5, 6, 7, 8, 9]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        for i in self.area_list:
            data = {'districtID': i}
            res = requests.post(url='http://www.fangdi.com.cn/complexPro.asp', data=data)
            html_str = res.content.decode('gbk')
            # 根据返回结果 获取每个地区的返回分页
            url_list = re.findall('value="(/complexpro.*?)"', html_str, re.S | re.M)
            for k in url_list:
                response = requests.get('http://www.fangdi.com.cn' + k, headers=self.headers)
                html = response.content.decode('gbk')
                comm_html = re.search('位置<.*?页/共', html, re.S | re.M).group()
                comm_info_list = re.findall('<tr valign=.*?</tr>', comm_html, re.S | re.M)
                for info in comm_info_list:
                    try:
                        comm = Comm(co_index)
                        comm_url = re.search('<a href=(.*?)>', info, re.S | re.M).group(1)
                        comm.co_name = re.search('<a.*?>(.*?)<', info, re.S | re.M).group(1)
                        comm.co_address = re.search('<a.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                        comm.co_all_house = re.search('<a.*?<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                        comm.co_all_size = re.search('<a.*?<td.*?<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                        comm.area = re.search('<a.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', info, re.S | re.M).group(1)
                        comm.co_id = re.search('projectID=(.*?)==', info, re.S | re.M).group(1)
                        self.get_comm_info(comm_url, comm)
                    except Exception as e:
                        print('小区错误，co_index={},url={}'.format(co_index, 'http://www.fangdi.com.cn' + k), e)

    def get_comm_info(self, comm_url, comm):
        co_url = 'http://www.fangdi.com.cn/' + comm_url
        response = requests.get(co_url, headers=self.headers)
        html = response.content.decode('gbk')
        comm.co_develops = re.search('企业名称：.*?<a.*?>(.*?)<', html, re.S | re.M).group(1)
        comm.insert_db()
        add_build_url = 'http://www.fangdi.com.cn/Presell.asp?projectID=' + comm.co_id
        result = requests.get(add_build_url, headers=self.headers)
        html_str = result.content.decode('gbk')
        build_detail_tuple_list = re.findall("javascript:SetSelect\(.*?,.*?,.*?,.*?,.*?,'(.*?)','(.*?)'\)", html_str,
                                             re.S | re.M)
        for i in build_detail_tuple_list:
            PreSell_ID = i[0]
            Start_ID = i[1]
            build_detail_url = 'http://www.fangdi.com.cn/building.asp?ProjectID=OTU4OHwyMDE4LTQtNHwxNw&PreSell_ID=' + PreSell_ID + '&Start_ID=' + Start_ID
            massage = requests.get(build_detail_url, headers=self.headers).content.decode('gbk')
            build_url_list = re.findall('class="indextabletxt">.*?</tr>', massage, re.S | re.M)
            for i in build_url_list:
                try:
                    build = Building(co_index)
                    build.bu_num = re.search('<a.*?>(.*?)</a>', i, re.S | re.M).group(1)
                    build.bu_all_house = re.search('<a.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_build_size = re.search('<a.*?<td.*?<td.*?<td.*?<td.*?>(.*?)<', i, re.S | re.M).group(1)
                    build.bu_id = re.search('Param=(.*?)=', i, re.S | re.M).group(1)
                    build.co_id = comm.co_id
                    build.insert_db()
                    house_url = re.search('href="(.*?)"', i, re.S | re.M).group(1)
                    self.get_house_info(house_url, build.bu_id, build.co_id)
                except Exception as e:
                    print('楼栋错误，co_index={},url={}'.format(co_index, build_detail_url), e)

    def get_house_info(self, house_url, bu_id, co_id):
        ho_url = 'http://www.fangdi.com.cn/' + house_url
        response = requests.get(ho_url, headers=self.headers)
        html = response.content.decode('gbk')
        house_html = re.search('室号 <.*?</table>.*?</table>', html, re.S | re.M).group()
        house_info_list = re.findall('title.*?</td>', house_html, re.S | re.M)
        for i in house_info_list:
            try:
                house = House(co_index)
                house.ho_build_size = re.search('实测面积:(.*?)>', i, re.S | re.M).group(1)
                house.ho_name = re.search('实测面积.*?>(.*?)<br>', i, re.S | re.M).group(1).strip()
                house.bu_id = bu_id
                house.co_id = co_id
                if '<a' in house.ho_name:
                    house_detail_url_code = re.search('href="(.*?)"', house.ho_name, re.S | re.M).group(1)
                    house_detail_url = 'http://www.fangdi.com.cn/' + house_detail_url_code
                    result = requests.get(house_detail_url, headers=self.headers)
                    html_str = result.content.decode('gbk')
                    house.ho_floor = re.search('实际层.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_name = re.search('室号.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_type = re.search('房屋类型.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_room_type = re.search('房型.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_build_size = re.search('实测建筑面积.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_true_size = re.search('实测套内面积.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                    house.ho_share_size = re.search('实测分摊面积.*?<TD.*?>(.*?)<', html_str, re.S | re.M).group(1)
                house.insert_db()
            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, ho_url), e)
