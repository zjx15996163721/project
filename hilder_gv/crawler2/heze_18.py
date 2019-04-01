import requests
import re
from lxml import etree
from backup.comm_info import Comm, Building, House
from backup.crawler_base import Crawler

co_index = '18'


class Heze(Crawler):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            "Referer": "http://www.hzszjj.gov.cn/ts_web_dremis/web_house_dir/Show_GoodsHouse_More.aspx",
            'Host': "www.hzszjj.gov.cn",
            'Connection': "keep-alive",
            'Content-Length': "24682",
            'Cache-Control': "max-age=0",
            'Origin': "http://www.hzszjj.gov.cn",
            'Upgrade-Insecure-Requests': "1",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Referer': "http://www.hzszjj.gov.cn/ts_web_dremis/web_house_dir/Show_GoodsHouse_More.aspx",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Cookie': "ASP.NET_SessionId=k4cx0lbhod14he55ok3sxfzl",
            'Content-Type': "application/x-www-form-urlencoded",

        }

        self.url = "http://www.hzszjj.gov.cn/ts_web_dremis/web_house_dir/Show_GoodsHouse_More.aspx"

    def total_page(self):  # 总页数
        res = requests.get(self.url)
        content = res.text
        html = etree.HTML(content)
        num_page = html.xpath("//div[@id='ctl00_ContentPlaceHolder2_AspNetPager1']/a/@href")[10]
        pattern = re.compile(r"'\d+'")
        page_num = pattern.search(num_page).group(0)
        page_num = int(page_num.strip("''"))
        return page_num

    def crawler(self):  # 列表页
        page = self.total_page()

        list_formdata = {}
        for i in range(1, page + 1):

            list_formdata["__EVENTTARGET"] = "ctl00$ContentPlaceHolder2$AspNetPager1"

            list_formdata["__EVENTARGUMENT"] = i

            res = requests.post(self.url, data=list_formdata, headers=self.headers)
            content = etree.HTML(res.text)
            href_list = content.xpath("//td[@class='SteelBlueSize']/a/@href")
            view_state = content.xpath("//input[@name='__VIEWSTATE']/@value")[0]
            valid = content.xpath("//input[@name='__EVENTVALIDATION']/@value")[0]

            list_formdata["__VIEWSTATE"] = view_state  # 保存当前页的信息作为下一页请求参数
            list_formdata["__EVENTVALIDATION"] = valid
            # view_state = urllib.parse.quote(view_state)
            # valid = urllib.parse.quote(valid)

            for href in href_list:
                pattern = re.compile(r"javascript\:.*?Back\('(.*?)'")
                data = pattern.search(href).group(1)

                # data = urllib.parse.quote(data)
                formdata = {}
                formdata["__EVENTTARGET"] = data
                formdata["__VIEWSTATE"] = view_state
                formdata["__EVENTVALIDATION"] = valid  # 详情页表单参数

                res = requests.post(self.url, data=formdata, headers=self.headers)

                con = etree.HTML(res.text)
                return con

    def room_crawler(self, room):  # 房屋

        ho = House(co_index)

        house_url = "http://www.hzszjj.gov.cn" + room

        res = requests.get(house_url, )
        con = etree.HTML(res.text)

        ho_table = con.xpath("//tr[@bgcolor='#fbf3e6']")
        for ho_list in ho_table[1:-1]:
            ho_floor = ho_list.xpath("./td[@align='center']/text()")[0]
            honum_list = ho_list.xpath(".//tr/td[@height='40']")
            for house in honum_list:
                ho.ho_floor = ho_floor  # 楼层
                id_num = re.search(r"(\d+)&\w+=(\d+)", room)
                ho.co_id = id_num.group(1)  # 小区id
                ho.bu_id = id_num.group(2)  # 楼栋id
                ho_url = house.xpath("./a/@href")[0]
                if len(ho_url) == 1:
                    ho_info = house.xpath("./a/@wf")[0]

                    ho.ho_name = house.xpath("./a/text()")[0]
                    info = re.search(r"：(.*?)<br>.*?：(.*?)<br>(.*?)<br><hr>.*?:(.*?)m.*?<br>.*?:(.*?)<br>.*?:(.*?)m",
                                     ho_info)
                    ho.ho_type = info.group(5)
                    ho.ho_build_size = info.group(4)
                    ho.ho_room_type = info.group(2)

                else:
                    detail_url = "http://www.hzszjj.gov.cn/ts_web_dremis/web_house_dir/" + ho_url
                    res = requests.get(detail_url)
                    con = etree.HTML(res.text)
                    ho.ho_name = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_house_name']/text()")[0]
                    ho.ho_type = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_house_type']/text()")[0]
                    ho.ho_build_size = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_house_build_area']/text()")[
                        0]
                    ho.ho_share_size = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_house_share_area']/text()")[
                        0]
                    ho.ho_true_size = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_house_inside_area']/text()")[
                        0]

                ho.insert_db()

    def comm_info(self, con, ):
        # 小区及楼栋
        comm = Comm(co_index)

        comm.co_name = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_web_item_retail1_lb_item_name']/text()")[
            0]  # 小区名称
        co_id_str = con.xpath("//form[@id='aspnetForm']/@action")[0]  # 小区id
        comm.co_id = re.search(r"\d+", co_id_str).group(0)
        comm.co_address = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_item_seat']/text()")[0]  # 小区地址
        comm.co_develops = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_enter_name']/text()")[0]  # 开发商
        comm.co_size = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_area']/text()")[0]  # 总面积
        comm.co_build_size = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_item_area']/text()")[0]  # 建筑面积
        comm.co_build_end_time = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_item_ew_date']/text()")[0]  # 竣工时间
        comm.co_plan_pro = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_program_pcode']/text()")[0]  # 用地规划许可
        comm.co_work_pro = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_jg']/text()")[0]  # 施工许可
        comm.co_green = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_item_green_rate']/text()")[0]  # 绿地百分比
        comm.co_land_use = con.xpath("//span[@id='ctl00_ContentPlaceHolder2_lb_td']/text()")[0]  # 土地使用证

        comm.insert_db()

        build = Building(co_index)
        build_table = con.xpath("//tr[@style='color:#000066;']")
        room_list = []
        for build_list in build_table:
            build.co_id = comm.co_id
            build.co_name = comm.co_name
            build_info = build_list.xpath("./td/text()")
            build.bu_id = build_info[0]
            build.bu_num = build_info[1]
            build.bu_all_house = build_info[2]
            build.size = build_info[3]
            build.bu_floor = build_info[4]
            build.bu_pre_sale = build_info[5]

            build.insert_db()

            room_url = build_list.xpath("./td/a/@href")[0]
            room_list.append(room_url)

        return room_list

    def start_crawler(self):
        con = self.crawler()
        room_list = self.comm_info(con)
        for room in room_list:
            self.room_crawler(room)


if __name__ == '__main__':
    a = Heze()
    a.start_crawler()
