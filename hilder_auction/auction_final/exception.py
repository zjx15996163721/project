class ConnectErrorException(Exception):
    """
        队列连接异常类
    """

    def __init__(self, err):
        Exception.__init__(self)
        self.err = err

    def __str__(self):
        return self.err


class ParseErrorException(Exception):
    """
        解析失败异常类
    """

    def __init__(self, err):
        Exception.__init__(self)
        self.err = err

    def __str__(self):
        return self.err
