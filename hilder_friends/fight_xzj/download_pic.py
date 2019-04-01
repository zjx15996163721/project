from gevent import monkey
monkey.main()
import requests
# from lib.proxy_iterator import Proxies
import threading
import gevent
import aiohttp
import asyncio


def run():
    loop = asyncio.get_event_loop()
    tasks = [start_request(num) for num in range(1000)]
    loop.run_until_complete(asyncio.wait(tasks))


async def start_request(num):
    await url_request(num)


async def url_request(num):
    url = 'http://www.xiaozijia.cn/user/GetVerifyCode'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            print(num)
            print(response)


def download_pic(num):
    url = 'http://www.xiaozijia.cn/User/GetVerifyCode'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    }
    r = requests.get(url=url, headers=headers)
    img = r.content
    with open('./pic/{}.png'.format(str(num)), 'wb') as f:
        f.write(img)
        print('下载一张图片{}'.format(num))


if __name__ == '__main__':
    count = 0
    count_list = []
    while True:
        count += 1
        count_list.append(count)
        if len(count_list) == 10000:
            tasks = [gevent.spawn(download_pic, num) for num in count_list]
            gevent.joinall(tasks)
            count_list.clear()
        else:
            continue






