from abc import ABC, abstractmethod


class Crawler(ABC):
    @abstractmethod
    def start_crawler(self):
        print('未实现crawler_base方法')
        raise NotImplementedError
    #
    # @abstractmethod
    # def comm_url_list(self, comm_url_list):
    #     print('未实现comm_url_list方法')
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def build_url_list(self, build_url_list):
    #     print('未实现build_url_list方法')
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def house_url_list(self, house_url_list):
    #     print('未实现house_url_list方法')
    #     raise NotImplementedError
