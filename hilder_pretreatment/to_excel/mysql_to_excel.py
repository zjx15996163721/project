from pymysql import connect
import pandas as pd
from datetime import datetime


class MysqlToexcel:

    def __init__(self, host, port, username, password, db, table):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        self.table = table

    def mysql_connect(self):
        conn = connect(host=self.host, port=self.port, user=self.username, password=self.password, db=self.db, charset='utf8')
        return conn

    def to_excel(self, **kwargs):
        conn = self.mysql_connect()
        cur =conn.cursor()

        filename = kwargs.get('filename', None)
        if not filename:
            filename = str(self.table) + str(datetime.now())[:10].replace('-', '')

        cur.execute("select count(*) from {}".format(self.table))
        num = cur.fetchone()[0]
        print(num)
        if num > 1500000 and kwargs.get('out_put') is not True:
            print('...所查询数据过多，建议按条件分批导出，若执意导出，请添加out_put为True')
            return False
        #
        # if kwargs == {}:
        #     return pd.read_sql("select * from")

if __name__ == '__main__':
    mx = MysqlToexcel('192.168.0.235',3336,'root','goojia7102','data_quality', 'city_coverage')
    mx.to_excel()