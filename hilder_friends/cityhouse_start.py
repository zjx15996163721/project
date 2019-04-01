from cityhouse.producer import CityHouseProducer
from cityhouse.consumer import CityHouseConsume
from multiprocessing import Process
from cityhouse.consumer_error_supply import comm_supply
if __name__ == '__main__':
    # c = CityHouseProducer()
    # c.start_produce()
    a = CityHouseConsume()
    a.start_consume()
    # comm_supply()
    # Process(target=c.start_produce).start()
    # Process(target=a.start_consume).start()