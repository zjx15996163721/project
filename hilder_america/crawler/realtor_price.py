import re
import asyncio
import aiohttp
import json
import pika
from lib.log import LogHandler
from lib.proxy_iterator import Proxies

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673))

log = LogHandler(__name__)
p = Proxies()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36', }

source = 'realtor'


class Consumer:
    def __init__(self):
        self.proxy = 'http://FANGJIAHTT7:HGhyd7BF@http-proxy-sg2.dobel.cn:9180'

    def start_consume(self):
        channel = connection.channel()
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(self.callback,
                              queue='soldprice',
                              )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        url_list = json.loads(body.decode())
        semaphore = asyncio.Semaphore(12)
        loop = asyncio.get_event_loop()
        tasks = [self.proxy_request(url,semaphore) for url in url_list]
        loop.run_until_complete(asyncio.wait(tasks))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('放入sold队列')

    async def proxy_request(self, url,semaphore):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, headers=headers, proxy=next(p)['http']) as resp:
                        if resp.status == 200:
                            con = await resp.text()
                            if 'Your IP address has been blocked' in con:
                                log.error('ip is banned,url={}'.format(url))
                            else:
                                co_id = re.search('property-overview/(.*)', url).group(1)
                                await self.new_queue((con,co_id))
                        else:
                            log.error('{}请求失败,code={}'.format(url,resp.status))
                except Exception as e:
                    log.error('{}请求失败={}'.format(url,e))
                    await self.proxy_request(url,semaphore)

    @staticmethod
    async def new_queue(con):
        result = json.dumps(con)
        channel = connection.channel()
        channel.queue_declare(queue='sold_result')
        channel.basic_publish(exchange='', routing_key='sold_result', body=json.dumps(result))
