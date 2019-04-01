import requests
from qiniu import Auth, put_file, etag
import uuid
from lib.log import LogHandler

# from qiniu.auth import digest
"""
    七牛云自带的图片爬取功能
"""
# def qiniufetch(url, bucket, filename):
#     """调用七牛的fetch API 将url的图片存储到七牛"""
#     access_key = "qjku2wyeTzY-yXiQ3JuTvkT87kn4OBdrA3VnK46e"
#     secret_key = "JHbwSYk-0e2GqzH8--H-AO9X12BiNYq-qbAdzLY7"
#     bucket_domain = 'http://p6cbf0l2n.bkt.clouddn.com'
#     auth = Auth(access_key, secret_key)
#     # 初始化BucketManager
#     bucket_manager = BucketManager(auth)
#     ret, info = bucket_manager.fetch(url,bucket,filename)
#     if info.status_code == 200:
#
#         file_url = bucket_domain + "/" + filename
#         print(file_url)
#         return file_url
#     else:
#         print("{}抓取失败".format(url))
"""
    图片爬取
"""
proxies = [{"http": "http://192.168.0.96:3234"},
                        {"http": "http://192.168.0.93:3234"},
                        {"http": "http://192.168.0.90:3234"},
                        {"http": "http://192.168.0.94:3234"},
                        {"http": "http://192.168.0.98:3234"},
                        {"http": "http://192.168.0.99:3234"},
                        {"http": "http://192.168.0.100:3234"},
                        {"http": "http://192.168.0.101:3234"},
                        {"http": "http://192.168.0.102:3234"},
                        {"http": "http://192.168.0.103:3234"}, ]
bucket = 'articleimage'
log = LogHandler("qiniu")

def qiniufetch(url,file_name):

    headers={"user_agent":
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
    }
    if 'http://' or 'https://' in url:
        """
            使用代理池
        """
        # image_download = Proxy_contact(app_name='qiniufetch', method='get', url=url, headers=headers)
        # con = image_download.contact()
        # while True:
        #     try:
        #         proxy = proxies[random.randint(0, 9)]
        #         res = requests.get(url, headers=headers, proxies=proxy, timeout=10)  # 图片连接请求
        #         con = res.content
        #         if res.status_code == 200:
        #             break
        #         else:
        #             continue
        #     except Exception as e:
        #         print(e)
        # if con == False:
        #     return None
        try:
            res = requests.get(url, headers=headers,timeout=10)
            con = res.content
        except:
            return False
        with open('article.jpg', 'wb') as f:
            f.write(con)
    else:
        try:
            img_url = 'http:'+url
            res = requests.get(img_url, headers=headers, timeout=10)
            con = res.content
            with open('article.jpg', 'wb') as f:
                f.write(con)
        except:
            log.info('图片格式不标准')
            return False

    filename = uuid.uuid3(uuid.NAMESPACE_DNS, file_name)

    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'qjku2wyeTzY-yXiQ3JuTvkT87kn4OBdrA3VnK46e'
    secret_key = 'JHbwSYk-0e2GqzH8--H-AO9X12BiNYq-qbAdzLY7'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = bucket
    # 上传到七牛后保存的文件名
    key = str(filename)
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    # 要上传文件的本地路径
    localfile = './article.jpg'
    ret, info = put_file(token, key, localfile)
    # print(info)
    while True:
        try:
            assert ret['key'] == key
            assert ret['hash'] == etag(localfile)
            break
        except:
            continue

    log.info('上传图片{}成功'.format(filename))
    bucket_domain = 'http://p6cbf0l2n.bkt.clouddn.com'
    file_url = bucket_domain + "/" + str(filename)
    return file_url