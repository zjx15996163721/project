from sh_wuye.mongo_and_rabbit import Monbbit
from multiprocessing import Process
from sh_wuye.get_all_community import consume_queue as get_all_comm
from sh_wuye.get_building_id import consume_queue as con_build
from sh_wuye.get_detail_info import consume_queue as con_detail
from sh_wuye.get_house_num import consume_queue as con_house

if __name__ == '__main__':
    # 放入key_name
    m = Monbbit('wuye', 'key_name', 'key_name', '_id',
                m_host='114.80.150.196', r_host='127.0.0.1'
                )
    m.put_rabbit()
    for i in range(10):
        Process(target=get_all_comm).start()
    for i in range(10):
        Process(target=con_build).start()
    for i in range(10):
        Process(target=con_detail).start()
    for i in range(10):
        Process(target=con_house).start()
