from big_city.soufang_consumer import SouFangConsumer
import threading

if __name__ == '__main__':
    for i in range(50):
        soufang = SouFangConsumer()
        threading.Thread(target=soufang.start_consuming).start()