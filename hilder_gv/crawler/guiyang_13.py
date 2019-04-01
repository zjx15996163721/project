

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re
import requests
from  lxml import etree

url = 'http://www.gyfc.net.cn/2_proInfo/index.aspx'
co_index = '13'
city = '贵阳'


class Guiyang(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36'
        }

    def start_crawler(self):
        all_url = AllListUrl(first_page_url=url, page_count_rule='总页数.*?<b>(.*?)</b>',
                             analyzer_type='regex',
                             request_method='get',
                             headers=self.headers,
                             encode='gbk')
        # 所有分页
        page_count = all_url.get_page_count()
        all_url_list = []
        for i in range(1, page_count + 1):
            all_url_list.append('http://www.gyfc.net.cn/2_proInfo/index.aspx/?page=' + str(i))
        print(all_url_list)

        self.get_comm_info(all_url_list)
        # 获取所有楼栋列表页 http://www.gyfc.net.cn/pro_query/index.aspx?yszh=2017005&qu=2

    def get_comm_info(self, all_url_list):
        for i in all_url_list:
            res = requests.get(i,headers=self.headers)
            con = res.content.decode('gbk')
            current_url_list = re.findall('<a href="(.*?)"  target="_blank">查看详细',con)
            for current_url in current_url_list:
                co_id = re.search('id=(\d+)',current_url).group(1)
                res = requests.get(current_url,headers=self.headers)
                con = res.content.decode('gbk')
                if '尾页' in con:
                    b = AllListUrl(first_page_url=current_url, page_count_rule='总页数.*?<b>(\d+)</b>',
                             analyzer_type='regex',
                             request_method='get',
                             headers=self.headers,
                             encode='gbk')

                    page_count = b.get_page_count()
                    for i in range(1,int(page_count)+1):
                        url =  current_url + "&page=" + str(i)
                        comm_page = requests.get(url,headers=self.headers)
                        comm_con = comm_page.content.decode('gbk')
                        self.comm_info_parse(comm_con,co_id)
                else:
                    self.comm_info_parse(con,co_id)

    def comm_info_parse(self,comm_page,co_id):
        comm = Comm(co_index)
        detail_url_list = re.findall('预售证号.*?href="(.*?)" target', comm_page,re.S|re.M)[1:]

        for detail_url in detail_url_list:
            try:
                detail_res = requests.get(detail_url, headers=self.headers)
            except Exception as e:
                print("co_index={},小区{}请求失败".format(co_index,detail_url))
                print(e)
                continue
            detail_con = detail_res.content.decode('gbk')
            try:
                comm.co_id = co_id
                comm.co_name = re.search('项目名称.*?>(.*?)</span>', detail_con).group(1)
                comm.co_type = re.search('性质.*?">(.*?)<', detail_con, re.S | re.M).group(1)
                comm.co_develops = re.search('开发商：.*?">(.*?)</', detail_con, re.S | re.M).group(1)
                comm.co_build_size = re.search('建筑面积：.*?listJZMJ">(.*?)</span', detail_con, re.S | re.M).group(1)
                comm.co_size = re.search('占地面积：.*?litZDMJ">(.*?)</span', detail_con, re.S | re.M).group(1)
                comm.co_land_use = re.search('土地使用权证号：.*?5" >(.*?)</td', detail_con, re.S | re.M).group(1)
                comm.co_plan_useland = re.search('用地规划许可证号：.*?" >(.*?)</td>', detail_con, re.S | re.M).group(1)
                comm.co_plan_project = re.search('工程规划许可证号：.*?" >(.*?)</td>', detail_con, re.S | re.M).group(1)
                comm.co_work_pro = re.search('施工许可证号：.*?">(.*?)</td>', detail_con, re.S | re.M).group(1)
                comm.insert_db()
            except Exception as e:
                continue

            bu_list_url = detail_url.replace('index','donginfo')
            bu_pre = re.search('yszh=(.*?)&',bu_list_url).group(1)
            try:
                bu_res = requests.get(bu_list_url,headers=self.headers)
            except Exception as e:
                print("co_index={},楼栋url{}未请求到".format(co_index,bu_list_url))
                print(e)
                continue
            bu_con = bu_res.content.decode('gbk')
            self.get_build_info(bu_con,co_id,bu_pre)


    def get_build_info(self,bu_con,co_id,bu_pre):
        bu = Building(co_index)
        bu_info = etree.HTML(bu_con)
        for i in bu_info.xpath("//table[@id='ContentPlaceHolder1_dong_info1_dg1']//tr")[2:-1]:
            bu.bu_id = i.xpath("./td/text()")[0]
            bu.bu_num = i.xpath("./td/text()")[1]
            bu.bu_all_house = i.xpath("./td/text()")[2]
            bu.bu_pre_sale = bu_pre
            bu.co_id = co_id
            bu.insert_db()
            # house_url = i.xpath("./td/a/@href")[0]
            house_url = "http://www.gyfc.net.cn/pro_query/index/floorView.aspx?dongID="+str(bu.bu_id)+"&danyuan=%C8%AB%B2%BF&qu=%B9%F3%D1%F4"+"&yszh="+str(bu_pre)
            try:
                house_info = requests.get(house_url,headers=self.headers)
            except Exception as e:
                print("co_index={},房屋详情页{}请求失败".format(co_index,house_url))
                print(e)
                continue
            self.get_house_info(house_info,bu.bu_id,co_id)

    def get_house_info(self,house_info,bu_id,co_id):
        ho = House(co_index)
        house_con = house_info.content.decode('gbk')
        for k in re.findall('<div class.*?</table></div>', house_con, re.S | re.M)[1:]:
            try:
                if '层' in k:
                    continue
                if '单元' in k:
                    continue
                else:
                    ho.ho_build_size = re.search('title.*\n(.*?)\n',k).group(1)
                    ho.bu_id = bu_id
                    ho.co_id = co_id
                    if '室'or'厅' in k:
                        ho.ho_room_type = re.search("\n(.*?)\\'><table",k).group(1)
                    else:
                        ho.ho_room_type = None

                    ho.ho_type = re.search('title=.*?\n(.*?)\n(.*?)\n(.*?)',k).group(2)

                    ho.ho_name = re.search("<span class=.*?>(.*?)</span>",k).group(1)
                    ho.insert_db()
            except Exception as e:
                print(e, k)
                continue
