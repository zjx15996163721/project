from youda_res.youda import Record
from dbfread import DBF
from youda_res.youda_match_insert import YouData


if __name__ == '__main__':
    # """
    # 需要把cjxx_3.DBF文件放到相同路径下
    # """
    # table = DBF('cjxx_3.DBF', recfactory=Record, ignore_missing_memofile=True)
    # for record in table:
    #     record.insert()

    youda = YouData('友达')

    # """
    # 地址去除室号，小区名切分成list
    # """
    # youda.format()
    # """
    # 匹配城市区域小区名
    # """
    # youda.match()
    # """
    # 入43成交库
    # """
    youda.insert_43()

