from auction_final.pipeline import Pipe


class AliConsumer(Pipe):
    """
        阿里拍卖最终入库解析
    """

    def __init__(self):
        super(Pipe, self).__init__()
        self.queue = 'ali_parse'
        self.routing_key = 'ali_parse'

    def callback(self, ch, method, properties, body, ):
        msg = body.decode()
        self.parse(msg)

    def parse(self, msg):
        pass


class JindongConsumer(Pipe):
    """
        京东拍卖最终入库解析
    """

    def __init__(self):
        super(Pipe, self).__init__()
        self.queue = 'jindong_parse'
        self.routing_key = 'jingdong'

    def callback(self, ch, method, properties, body, ):
        msg = body.decode()
        self.parse(msg)

    def parse(self, msg):
        pass


if __name__ == '__main__':
    ali = AliConsumer()
    jingdong = JindongConsumer()
    ali.start_consume()
    jingdong.start_consume()
