from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import requests, re
from lxml import etree

co_index = '38'
city = '清远'


class Qingyuan(Crawler):
    def __init__(self):
        self.start_url = 'http://www.qyfgj.cn/newys/user_kfs.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Cookie':
                'ASP.NET_SessionId=irv0qjamqztp1pb0shoqrx2j',
            'Referer':
                'http://www.qyfgj.cn/newys/user_itemlist.aspx?key=&kind=&LID={6900FCBE-7A85-4447-A188-E9A056777415}'
        }
        self.url = 'http://www.qyfgj.cn/newys/user_itemlist.aspx?key=&kind=&LID={6900FCBE-7A85-4447-A188-E9A056777415}&page='

    def start_crawler(self):
        n = 1
        while True:
            page_url = self.url + str(n)
            res = requests.get(page_url,headers=self.headers)
            con = res.content.decode('gbk')
            if '找不到信息' in con:
                break
            else:
                ret = re.findall('<tr bg(.*?)</tr>',con,re.S|re.M)
                for i in ret:
                    self.get_comm_info(i)
            n = int(n)
            n +=1
    def get_comm_info(self,comm_info):

        co = Comm(co_index)
        co.co_name = re.search('_blank">(.*?)</a',comm_info).group(1)
        try:
            co.co_address = re.findall('px">(.*?)</td',comm_info)[1]
        except:
            co.co_address = None
        co.area = re.search('center">(.*?)</td>',comm_info).group(1)
        co_detail_url = re.search("href='(.*?)'",comm_info).group(1)
        co_url = "http://www.qyfgj.cn/newys/"+co_detail_url
        try:
            res = requests.get(co_url,headers=self.headers)
        except Exception as e:
            print("co_index={}小区未请求到".format(co_index),e)
        con = res.content.decode('gbk')
        try:
            co.co_develops = re.search('开发商名称.*?px;">(.*?)</a',con,re.S|re.M).group(1)
            co.co_all_house = re.search('总套数.*?">(\d+)&nbsp',con,re.S|re.M).group(1)
            co.co_all_size = re.search('总面积.*?">(\d+.\d+)&nbsp;m',con,re.S|re.M).group(1)
        except:
            print("小区无开发商等信息")
        co.insert_db()

        try:
            build = re.findall('<tr bgcolor="white">(.*?)</tr>',con,re.S|re.M)
        except:
            print("小区没有楼栋信息")
        build_headers = {'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Cookie':
                'ASP.NET_SessionId=irv0qjamqztp1pb0shoqrx2j',
            'Referer':
                co_url
        }

        for build_info in build:
            if "进入" in build_info:
                build_url = re.search('href="(.*?)"><font',build_info).group(1)
                build_url = "http://www.qyfgj.cn/newys/" + build_url
                ho_headers={
                    'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
                    'Cookie':
                        'ASP.NET_SessionId=irv0qjamqztp1pb0shoqrx2j',
                    'Referer':
                        build_url
                }
                build_res = requests.get(build_url, headers=build_headers)
                build_con = build_res.content.decode('gbk')

                if re.search('ID=(\d+)',build_url):   #现售
                    bu = Building(co_index)
                    bu_id = re.search('ID=(\d+)',build_url).group(1)
                    bu.bu_id = bu_id
                    bu.co_name =co.co_name
                    bu.insert_db()
                    self.get_house_info(headers=ho_headers,bu_id=bu_id,url=build_url)

                else:                                  #预售
                    bu = Building(co_index)
                    bu.co_name = co.co_name
                    bu.bu_type = re.search('用途.*?">(.*?)</td>', build_con, re.S | re.M).group(1)
                    bu.bu_pre_sale = re.search('许可证编号.*?_blank">(.*?)</a>', build_con, re.S | re.M).group(1)
                    bu.bu_pre_sale_date = re.search('有效日期.*?">(.*?)</td>', build_con, re.S | re.M).group(1)
                    bu.bu_address = re.search('项目座落.*?">(.*?)</td>', build_con, re.S | re.M).group(1)
                    ret = re.findall('<tr onmouseover(.*?)</tr',build_con,re.S|re.M)
                    for i in ret:
                        house_url = re.search('href="(.*?)"',i).group(1)
                        house_url = "http://www.qyfgj.cn/newys/" + house_url
                        bu.bu_id = re.search('dbh=(.*?)&',i).group(1)
                        bu.bu_num = re.search('<td width="89.*?">(.*?)</',i).group(1)
                        bu.bu_floor = re.search('<td width="84.*?">(\d+)</td',i).group(1)
                        bu.insert_db()

                        ho_res = requests.get(house_url,headers=ho_headers)
                        ho_con = ho_res.content.decode('gbk')
                        new_headers = {
                            'User-Agent':
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
                            'Cookie':
                                'ASP.NET_SessionId=irv0qjamqztp1pb0shoqrx2j',
                            'Referer':
                                house_url
                        }
                        self.get_house_info(ho_con=ho_con,headers=new_headers,bu_id=bu.bu_id)
            else:
                print("楼栋无链接地址")

    def get_house_info(self,ho_con=None,headers=None,bu_id=None,url=None):

        if ho_con == None:
            res = requests.get(url, headers=headers)

            con = res.content.decode('gbk')
            html = etree.HTML(con)

        else:
            html = etree.HTML(ho_con)

        ho_url_list = html.xpath("//td[@width='120']/a/@href")

        for ho_url in ho_url_list:
            ho_detail = 'http://www.qyfgj.cn/newys/'+ho_url
            res = requests.get(ho_detail,headers=headers)
            con = res.content.decode('gbk')
            ho = House(co_index)

            ho.bu_id = bu_id
            ho.ho_num = re.search('房屋号.*?">(.*?)</td',con,re.S|re.M).group(1)
            ho.ho_build_size = re.search('建筑面积.*?">(.*?)m',con,re.S|re.M).group(1)
            ho.ho_true_size = re.search('套内面积.*?">(.*?)m',con,re.S|re.M).group(1)
            ho.ho_type = re.search('房屋用途.*?">(.*?)</td',con,re.S|re.M).group(1)

            ho.insert_db()