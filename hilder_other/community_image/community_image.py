import pymongo
from lxml import etree
import re
import bson


def get_pymongo_config(db_name, collection, ip, port):
    """
    :param db_name: 数据库名称
    :param collection: 表名称
    :return: mongodb collection
    """
    client = pymongo.MongoClient(ip, port)
    db = client[db_name]
    coll = db.get_collection(collection)
    return coll


def first_get():
    """
        5a30bb7ce4b0e452ecb4c4d4   搜房 全站 户型图
        :return:
    """
    count = 0
    coll = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    coll_put = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
    community_list = coll.find({'job_id': '5a30bb7ce4b0e452ecb4c4d4'})
    for i in community_list:
        try:
            job_id = i.get('job_id')
            content = i.get('data')['content']
            url = i.get('url')
            tree = etree.HTML(content)

            city = tree.xpath('//*[@id="huxinsy_E02_01"]/p/a[2]/text()')[0].replace('新房', '')
            area = tree.xpath('//*[@id="huxinsy_E02_01"]/p/a[3]/text()')[0].replace('楼盘', '')
            community = tree.xpath('//*[@id="huxinsy_E02_01"]/p/a[4]/text()')[0]
            image_list = []
            img_list = tree.xpath('//*[@id="huxinsy_E04_08"]')

            count += 1
            for img in img_list:
                img_url = img.xpath('a/img/@src')[0]
                roomtype = img.xpath('p[1]/a/span[1]/text()')[0]
                roomsize = img.xpath('p[1]/a/span[2]/text()')[0]
                size = re.search('(\d.*?)㎡', roomsize).group(1)
                imgs = {
                    'img': img_url,
                    'roomtype': roomtype,
                    'roomsize': size,
                }
                image_list.append(imgs)
            data = {
                'community': community,
                'city': city,
                'area': area,
                'image_list': image_list,
                'job_id': job_id,
            }
            print(data)
            coll_put.insert(data)
        except Exception as e:
            print('跳过一条错误页面')
            continue


def second_get():
    """
          5a30bbd1e4b0e452ecb4c4d6   安居客 全站 户型图
           :return:
    """
    collc = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    coll_put = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
    community_list = collc.find({'job_id': '5a30bbd1e4b0e452ecb4c4d6'})
    print(community_list.count())
    for i in range(community_list.count()):
        try:
            job_id = community_list[i].get('job_id')
            content = community_list[i].get('data')['content']
            url = community_list[i].get('url')
            print(url)
            tree = etree.HTML(re.search('<html>(.*?)html>', content, re.M | re.S).group())
            # tree = etree.HTML(content)
            city = tree.xpath('//*[@id="header"]/div[2]/div/a[2]/text()')[0].replace('楼盘', '').strip()
            area = tree.xpath('//*[@id="header"]/div[2]/div/a[3]/text()')[0].replace('楼盘', '').strip()
            community = tree.xpath('//*[@id="header"]/div[2]/div/a[4]/text()')[0].strip()
            image_list = []
            img_list = tree.xpath('//ul[@class="hx-list g-clear"]/li')
            for img in img_list:
                img_url = img.xpath('a/img/@imglazyload-src')[0]
                roomtype = img.xpath('div/div/div/span[2]/text()')
                roomsize = img.xpath('div/div[2]/span/text()')[0].strip()
                if roomtype:
                    roomtype = roomtype[0].strip()
                else:
                    roomtype = ''
                if '暂无' in roomsize:
                    size = '暂无'
                else:
                    size = re.search('约(.*?)m', roomsize, re.M | re.S)
                if not size:
                    size = '暂无'
                else:
                    size = size.group(1)
                imgs = {
                    'img': img_url,
                    'roomtype': roomtype,
                    'roomsize': size,
                }
                image_list.append(imgs)
            if not image_list:
                continue
            data = {
                'community': community,
                'city': city,
                'area': area,
                'image_list': image_list,
                'job_id': job_id,
            }
            print(data)
            coll_put.insert(data)
        except bson.errors.InvalidBSON as e:
            print('数据库乱码')


def third_get():
    """
        5a30bbd8e4b0e452ecb4c4d8    链家在线 全站 户型图
        :return:
    """
    count = 0
    collc = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    coll_put = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
    community_list = collc.find({'job_id': '5a30bbd8e4b0e452ecb4c4d8'})
    for i in community_list:
        try:
            job_id = i.get('job_id')
            url = i.get('url')
            content = i.get('data')['content']
            tree = etree.HTML(content)
            image_list = []
            if 'you.' in url:
                print(url)
                city = tree.xpath('//p[@class="zb_p_bread"]/span[2]/a/text()')[0].replace('房产', '')
                area = tree.xpath('//p[@class="zb_p_bread"]/span[3]/a/text()')[0].replace('楼盘', '')
                community = tree.xpath('//p[@class="zb_p_bread"]/span[4]/a/text()')[0]
                img_list = tree.xpath('//div[@id="frame_div_0"]/div')
                for img in img_list:
                    if not img:
                        continue
                    img_url = img.xpath('a/img/@src')[0]
                    roomtype = img.xpath('div/p/a/text()')
                    if roomtype:
                        roomtype = roomtype[0].strip()
                        type = re.search('(\d(.*?)卫)', roomtype).group(1)
                        size = re.search('面积(.*?)m²', roomtype).group(1)
                    else:
                        type = '暂无'
                        size = '暂无'
                    imgs = {
                        'img': img_url,
                        'roomtype': type,
                        'roomsize': size,
                    }
                    image_list.append(imgs)

                data = {
                    'community': community,
                    'city': city,
                    'area': area,
                    'image_list': image_list,
                    'job_id': job_id,
                }
            elif 'detail' in url:
                continue
            elif 'loupan' in url:
                print(url)
                city = tree.xpath('//div[@class="breadcrumbs"]/a[3]/text()')[0].replace('楼盘', '')
                area = tree.xpath('//div[@class="breadcrumbs"]/a[4]/text()')[0].replace('楼盘', '')
                community = tree.xpath('//div[@class="breadcrumbs"]/span[5]/text()')[0]
                img_list = tree.xpath('//*[@id="house-online"]/div[1]/div[1]/ul')
                for img in img_list:
                    img_url = img.xpath('li/img/@src')[0]
                    roomtype = img.xpath('li[2]/p[1]/text()')[0]
                    roomsize = img.xpath('li[2]/p[1]/span[1]/text()')[0]
                    size = re.search(r' (.*)m²', roomsize).group(1)
                    imgs = {
                        'img': img_url,
                        'roomtype': roomtype,
                        'roomsize': size,
                    }
                    image_list.append(imgs)
                data = {
                    'community': community,
                    'city': city,
                    'area': area,
                    'image_list': image_list,
                    'job_id': job_id,
                }
                print(data)
                coll_put.insert(data)
        except Exception as e:
            print(e)
            continue


def forth_get():
    """
        5a30bbe0e4b0e452ecb4c4da   新浪乐居 全站 户型图
        :return:
    """

    count = 0
    collc = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    coll_put = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
    community_list = collc.find({'job_id': '5a30bbe0e4b0e452ecb4c4da'})
    for i in community_list:
        try:

            job_id = i.get('job_id')
            url = i.get('url')
            print(url)
            content = i.get('data')['content']
            tree = etree.HTML(content)
            city = tree.xpath('/html/body/div[2]/div[2]/div/div[1]/a[2]/text()')[0].replace('楼盘', '')
            area = tree.xpath('/html/body/div[2]/div[2]/div/div[1]/a[3]/text()')[0].replace('楼盘', '')
            community = tree.xpath('/html/body/div[2]/div[2]/div/div[1]/a[2]/text()')[0]
            image_list = []
            img_list = tree.xpath('//ul[@class="b_list01 clearfix"]/li')
            for img in img_list:
                img_url = img.xpath('a/div/img/@lsrc')[0]
                if not img_url:
                    img_url = img.xpath('a/div/img/@src')[0]
                roomtype = img.xpath('a/div[2]/h2/span/text()')
                if roomtype:
                    roomtype = roomtype[0]
                else:
                    roomtype = '暂无'
                roomsize = img.xpath('a/div[2]/h3/text()')[0]
                if '暂无' in roomsize:
                    size = '暂无'
                else:
                    size = re.search(r'(.*)平', roomsize).group(1)
                imgs = {
                    'img': img_url,
                    'roomtype': roomtype,
                    'roomsize': size,
                }
                image_list.append(imgs)
            data = {
                'community': community,
                'city': city,
                'area': area,
                'image_list': image_list,
                'job_id': job_id,
            }
            print(data)
            coll_put.insert(data)
        except Exception as e:
            print('跳过一条错误页面')
            continue


def fifth_get():
    """
    5a30bbede4b0e452ecb4c4dc   搜狐焦点 全站 户型图
    :return:
    """
    coll_put = get_pymongo_config('buildings', 'community_image', '192.168.0.61', 27017)
    coll = get_pymongo_config('artemis', 'metadata', '192.168.0.188', 55007)
    all_ = coll.find({'job_id': '5a30bbede4b0e452ecb4c4dc'})
    for i in all_:
        try:
            list1 = []
            print(i['url'])
            url = i['url']
            html = i['data']['content']
            job_id = i['job_id']
            if '暂未找到相关内容' in html:
                continue
            else:
                tree = etree.HTML(html)
                if 'https' in url:
                    city = tree.xpath('//div[@class="bread-crumbs-area global-clearfix"]/span[2]/a/text()')[0].replace(
                        '楼盘', '')
                    area = tree.xpath('//div[@class="bread-crumbs-area global-clearfix"]/span[3]/a/text()')[0].replace(
                        '楼盘', '')
                    community = tree.xpath('//div[@class="bread-crumbs-area global-clearfix"]/span[3]/a/text()')[0]
                    img_info_list = tree.xpath('//dl[@class="tab-content global-clearfix"]/dd')
                    for img_info in img_info_list:
                        if not img_info:
                            continue
                        img_url = img_info.xpath('a/img/@src')[0]
                        roomtype = img_info.xpath('span/text()')[0].strip()
                        roomsize = ''
                        if roomtype:
                            roomtype = re.search(u'(\d室.*?卫)', roomtype).group(1)
                        else:
                            roomtype = '暂无'
                        img_infos = {
                            'img_url': img_url,
                            'roomtype': roomtype,
                            'roomsize': roomsize,
                        }
                        list1.append(img_infos)
                    data = {
                        'community': community,
                        'city': city,
                        'area': area,
                        'image_list': list1,
                        'job_id': job_id,
                    }
                    print(data)
                    # coll_put.insert(data)
                else:
                    area_info = tree.xpath('//div[@class="s-tag statis-log"]/a')
                    city = area_info[1].text.replace('楼盘', '')
                    area = area_info[2].text.replace('楼盘', '')
                    community = area_info[3].text
                    img_info_list = tree.xpath('//ul[@class="lp-hx"]/li')
                    for img_info in img_info_list:
                        img_url = img_info.xpath('a/div/img/@src')[0]
                        roomtype = img_info.xpath('a/div/p/text()')
                        roomsize = ''
                        if roomtype:
                            roomtype = roomtype[0]
                            roomtype = re.search(r'\d室(.*?)卫', roomtype).group()
                        else:
                            roomtype = '暂无'
                        img_infos = {
                            'img_url': img_url,
                            'roomtype': roomtype,
                            'roomsize': roomsize,
                        }
                        list1.append(img_infos)
                    if not list1:
                        continue
                    data = {
                        'community': community,
                        'city': city,
                        'area': area,
                        'image_list': list1,
                        'job_id': job_id,
                    }
                    print(data)
                    # coll_put.insert(data)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    # Thread(target=first_get).start()
    # Thread(target=second_get).start()
    # Thread(target=third_get).start()
    # Thread(target=forth_get).start()
    # Thread(target=fifth_get).start()
    fifth_get()
    second_get()
