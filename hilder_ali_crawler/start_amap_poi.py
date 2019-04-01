from multiprocessing import Process
from amap_poi.gevent_consumer_url_list import consume_all_url
# from amap_poi.produce_url import put_all_url_into_queue
# from amap_poi.producer_lat import put_lat_url_into_queue
from amap_poi.consume_result import ConsumeResult
from amap_poi.consume_page_list import consume_page_url

if __name__ == '__main__':
    # 1.将第一类url（城市和分类组合）放入amap_all_url队列,2.将第二种url（经纬度组合）放入amap_all_url队列
    # Process(target=put_all_url_into_queue).start()
    # Process(target=put_lat_url_into_queue).start()

    # 3.消费队列中的url,将结果存入到amap_result_json队列中，并将count值大于50的进行分页操作，将分页url从第二页开始存入到amap_all_url队列中
    Process(target=consume_all_url).start()

    # 4.消费分页队列中的url
    Process(target=consume_page_url).start()
    # 5.结果入库操作类的写法
    result = ConsumeResult()
    Process(target=result.consume_result).start()
