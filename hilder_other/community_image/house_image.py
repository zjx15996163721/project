import pymongo
import json
import time
from lxml import etree
import re
from threading import Thread
from bloomfilter_redis import BloomFilter



def get_pymongo_config(db_name, collection, ip, port):
    """
    :param db_name: 数据库名称
    :param collection: 表名称
    :return: mongodb collection
    """
    client = pymongo.MongoClient(ip, port, unicode_decode_error_handler='ignore')
    db = client[db_name]
    coll = db.get_collection(collection)
    return coll


def anjuke(anjuke_list):
    """
        安居客 户型图  559f2a7be4b0133c041de3d6  50c367dc4d60fd41bdae29b6
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    bf = BloomFilter()
    count = 0
    for i in anjuke_list:
        count += 1
        try:
            content = i['data']['content']
            if '安居客' not in content:
                print('luanma')
                continue
            if 'hd-tips' in content:
                print('sorry')
                continue
            url = i['url']
            image_list = []
            if bf.isContains(url):
                print('url重复')
                continue
            bf.insert(url)
            job_id = i['job_id']

            tree = etree.HTML(re.search('<html(.*?)html>', content, re.M | re.S).group())
            city = tree.xpath('//div[@id="content"]/div[1]/a[2]/text()')[0].replace('二手房', '').strip()
            area = tree.xpath('//div[@id="content"]/div[1]/a[3]/text()')[0].replace('二手房', '') \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            community = tree.xpath('//div[@id="content"]/div[1]/a[5]/text()')[0].strip() \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            roomtype = tree.xpath('//div[@class="houseInfoBox"]/div[1]/div[1]/div[1]/div[2]/dl[1]/dd/text()')[
                0].strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            roomsize = tree.xpath('//div[@class="houseInfoBox"]/div[1]/div[1]/div[1]/div[2]/dl[2]/dd/text()')[
                0].strip().replace('平方米', '')
            img_url = tree.xpath('//*[@id="hx_pic_wrap"]/div[@class="img_wrap"]/img/@src')
            for i in img_url:
                img = {
                    'img_url': i, 'roomtype': roomtype, 'roomsize': roomsize,
                }
                image_list.append(img)
            data = {
                'job_id': job_id,
                'city': city,
                'area': area,
                'community': community,
                'image_list': image_list
            }
            print(data)
            # coll_put.insert_one(data)
        except Exception as e:
            print(e)
            continue


def soufang(soufang_list):
    """
        搜房  5860cad9e4b09fa720084144  520d8513e4b0fb6103718fea  559f237de4b0e6f33e2bbb68  51025d0ae4b0bc9fcbe08173
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    bf = BloomFilter()
    for i in soufang_list:
        try:
            url = i['url']
            print(url)
            image_list = []
            if bf.isContains(url):
                print('url重复')
                continue
            bf.insert(url)
            job_id = i['job_id']
            content = i['data']['content']
            if '抱歉' in content or '很遗憾' in content:
                continue
            tree = etree.HTML(re.search('<html(.*?)html>', content, re.M | re.S).group())
            city = tree.xpath('//p[@id="agantesfxq_B01_04"]/a[2]/text()')[0].replace('二手房', '').strip()
            area = tree.xpath('//p[@id="agantesfxq_B01_04"]/a[3]/text()')[0].replace('二手房', '') \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            community = tree.xpath('//p[@id="agantesfxq_B01_04"]/a[5]/text()')[0].strip() \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '').replace('二手房', '')
            roomtype = tree.xpath('//div[@class="tab-cont-right"]/div[3]/div[1]/div[1]/text()')[
                0].strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            roomsize = tree.xpath('//div[@class="tab-cont-right"]/div[3]/div[2]/div[1]/text()')[
                0].strip().replace('平米', '')
            img_url = tree.xpath('//div[@class="cont-sty1 clearfix"]/div[1]/div/img[@alt="户型图"]/@data-src')
            if not img_url:
                img_url = tree.xpath('//div[@class="cont-sty1 clearfix"]/div[1]/div/img[@alt="户型图"]/@src')
            for i in img_url:
                img = {
                    'img_url': i, 'roomtype': roomtype, 'roomsize': roomsize,
                }
                image_list.append(img)
            data = {
                'job_id': job_id,
                'city': city,
                'area': area,
                'community': community,
                'image_list': image_list
            }
            print(data)
            # coll_put.insert_one(data)
        except Exception as e:
            print(e)
            continue


def lianjia(lianjia_list):
    """
    链家  510607e4e4b0bc9fcbe081db  559f309ce4b0133c041dea84
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    bf = BloomFilter()
    count = 0
    for i in lianjia_list:
        count += 1
        print(count)
        try:
            image_list = []
            job_id = i['job_id']
            url = i['url']
            content = i['data']['content']
            if '户型图' not in content:
                print('没有户型图')
                continue
            if '抱歉' in content or '很遗憾' in content:
                continue
            if bf.isContains(url):
                print('url重复')
                continue
            bf.insert(url)
            tree = etree.HTML(re.search('<html(.*?)html>', content, re.M | re.S).group())
            city = tree.xpath('//div[@class="fl l-txt"]/a[2]/text()')[0].replace('二手房', '').strip()
            area = tree.xpath('//div[@class="fl l-txt"]/a[3]/text()')[0].replace('二手房', '') \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            community = tree.xpath('//div[@class="fl l-txt"]/a[5]/text()')[0].strip() \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '').replace('二手房', '')
            roomtype = tree.xpath('//div[@class="houseInfo"]/div[1]/div[1]/text()')[
                0].strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            roomsize = tree.xpath('//div[@class="houseInfo"]/div[3]/div[1]/text()')[
                0].strip().replace('平米', '')
            img_url = tree.xpath('//div[@class="container"]/div/div/img/@src')
            for i in img_url:
                img = {
                    'img_url': i, 'roomtype': roomtype, 'roomsize': roomsize,
                }
                image_list.append(img)
            data = {
                'job_id': job_id,
                'city': city,
                'area': area,
                'community': community,
                'image_list': image_list
            }
            print(data)
            # coll_put.insert_one(data)
        except Exception as e:
            print(e)
            continue


def xinlang(xinlang_list):
    """
        新浪  540e6670e4b09e392f5bb2d4  559f31c8e4b0133c041df42a
    :param xinlang_list:
    :param coll_put:
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    bf = BloomFilter()
    for i in xinlang_list:
        try:
            url = i['url']
            print(url)
            image_list = []
            if bf.isContains(url):
                print('url重复')
                continue
            bf.insert(url)
            job_id = i['job_id']
            content = i['data']['content']
            if '此页面可能已被移走或已不存在' in content or '很遗憾' in content:
                print('404')
                continue
            tree = etree.HTML(re.search('<html(.*?)html>', content, re.M | re.S).group())
            city = tree.xpath('//nav[@class="nav-crumbs wrapin"]/a[2]/text()')[0].replace('二手房', '').replace('出售',
                                                                                                             '').strip()

            area = tree.xpath('//nav[@class="nav-crumbs wrapin"]/a[3]/text()')[0].replace('二手房', '') \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

            community = tree.xpath('//nav[@class="nav-crumbs wrapin"]/a[4]/text()')[0].strip() \
                .replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '').replace('二手房', '')
            roomtype = tree.xpath('//div[@class="panelB "]/table/tr[2]/td[2]/text()')[
                0].strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

            roomsize = tree.xpath('//div[@class="panelB "]/table/tr[2]/td[1]/text()')[
                0].strip().replace('平米', '')

            img_name = tree.xpath('//div[@class="h-pro-con"]/h4')
            for i in img_name:
                if i.xpath('text()')[0] == '户型图':
                    img_url = i.xpath('following-sibling::img[1]/@src')
                    print(img_url)
                    for i in img_url:
                        img = {
                            'img_url': i, 'roomtype': roomtype, 'roomsize': roomsize,
                        }
                        image_list.append(img)
                else:
                    continue
            if not image_list:
                print('没匹配到')
                continue
            data = {
                'job_id': job_id,
                'city': city,
                'area': area,
                'community': community,
                'image_list': image_list
            }
            print(data)
            # coll_put.insert_one(data)
        except Exception as e:
            print(e)
            continue


def tuitui99(fangyuan_list):
    """
    推推99  55406f33e4b0216fa3f282b8
    :return:
    """
    ff = BloomFilter()
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    for i in fangyuan_list:
        try:
            img_list = []
            job_id = i.get('job_id')
            content = i.get('data')['content']
            url = i.get('url')
            if ff.isContains(url):
                print('url重复')
                continue
            ff.insert(url)
            page = etree.HTML(content)
            city = page.xpath('//div[@class=" positi"]/div/a[2]/text()')[0].replace('二手房', '')
            region = page.xpath('//div[@class=" positi"]/div/a[3]/text()')[0].replace('二手房', '')
            community = \
                page.xpath('// *[ @ id = "listSourcePhoto"] / div[2] / ul / li[8] / div / span/text()')[0].split('（')[
                :-1][
                    0]
            roomtype = page.xpath('//*[@id="listSourcePhoto"]/div[2]/ul/li[3]/div[1]/span/text()')[0]
            roomsize = page.xpath('//*[@id="listSourcePhoto"]/div[2]/ul/li[3]/div[2]/span/text()')[0].replace('㎡', '')
            img_name = page.xpath('//html/body/div[4]/div[1]/div[6]/ul/li')
            for i in img_name:
                name = i.xpath('div[2]/text()')[0]
                if name == '户型图':
                    img_url = i.xpath('div/a/@href')
                    if img_url:
                        img_url = img_url[0]
                    # print(img_url)
                    img_dict = {
                        'roomtype': roomtype,
                        'roomsize': roomsize,
                        'img': img_url
                    }
                    img_list.append(img_dict)
                else:
                    continue
            if not img_list:
                continue
            analysis_data = {
                'job_id': job_id,
                'city': city,
                'area': region,
                'community': community,
                'image_list': img_list,
            }
            print(analysis_data)
            # coll_put.insert(analysis_data)
        except Exception as e:
            print(e)
            continue


def pinganhaofang(fangyuan_list):
    """
    平安好房  57fc4f19e4b06ef72e688c4f
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'house_image', '192.168.0.61', 27017)
    bf = BloomFilter()
    for i in fangyuan_list:
        try:
            img_list = []
            job_id = i.get('job_id')
            content = i.get('data')['content']
            url = i.get('url')
            if bf.isContains(url):
                print('url重复')
                continue
            bf.insert(url)
            page = etree.HTML(content)
            city = page.xpath('//*[@id="J_city"]/div/a/text()')[0]
            region = page.xpath('//html / body / div[4] / div[1] / a[3]/text()')[0].replace('二手房', '')
            community = page.xpath('//*[@id="xiaoquming"]/text()')[0]
            roomtype = page.xpath('// html / body / div[5] / div[1] / div[2] / div[1] / ul / li[5] / p[2]/text()')[0]
            roomsize = page.xpath('//html/body/div[5]/div[1]/div[2]/div[1]/ul/li[7]/p[2]/text()')[0].replace('m²', '')
            img = page.xpath('//*[@id="esfAlbum"]/li[@data-alt="房型图"]/img/@src')
            for i in img:
                img_dict = {
                    'roomtype': roomtype,
                    'roomsize': roomsize,
                    'img': i
                }
                img_list.append(img_dict)
            analysis_data = {
                'job_id': job_id,
                'city': city,
                'area': region,
                'community': community,
                'image_list': img_list
            }
            print(analysis_data)
            # coll_put.insert(analysis_data)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    coll = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    # # 安居客
    anjuke_list1 = coll.find({'job_id': '559f2a7be4b0133c041de3d6'})
    anjuke_list2 = coll.find({'job_id': '50c367dc4d60fd41bdae29b6'})
    Thread(target=anjuke, args=(anjuke_list1,)).start()
    Thread(target=anjuke, args=(anjuke_list2,)).start()
    # 搜房
    soufang_list1 = coll.find({'job_id': '5860cad9e4b09fa720084144'})
    soufang_list2 = coll.find({'job_id': '520d8513e4b0fb6103718fea'})
    soufang_list3 = coll.find({'job_id': '559f237de4b0e6f33e2bbb68'})
    soufang_list4 = coll.find({'job_id': '51025d0ae4b0bc9fcbe08173'})
    Thread(target=soufang, args=(soufang_list1,)).start()
    Thread(target=soufang, args=(soufang_list2,)).start()
    Thread(target=soufang, args=(soufang_list3,)).start()
    Thread(target=soufang, args=(soufang_list4,)).start()
    # 链家
    lianjia_list1 = coll.find({'job_id': '510607e4e4b0bc9fcbe081db'})
    lianjia_list2 = coll.find({'job_id': '559f309ce4b0133c041dea84'})
    Thread(target=lianjia, args=(lianjia_list1,)).start()
    Thread(target=lianjia, args=(lianjia_list2,)).start()
    # 新浪
    xinlang_list1 = coll.find({'job_id': '540e6670e4b09e392f5bb2d4'})
    xinlang_list2 = coll.find({'job_id': '559f31c8e4b0133c041df42a'})
    Thread(target=xinlang, args=(xinlang_list1,)).start()
    Thread(target=xinlang, args=(xinlang_list2,)).start()
    # 推推99
    tuitui99_list = coll.find({'job_id': '55406f33e4b0216fa3f282b8'})
    Thread(target=tuitui99, args=(tuitui99_list,)).start()
    # 平安好房
    pinganhaofang_list = coll.find({'job_id': '57fc4f19e4b06ef72e688c4f'})
    Thread(target=pinganhaofang, args=(pinganhaofang_list,)).start()
