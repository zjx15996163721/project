import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import json
import datetime
import time
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.models import MonitorProject, MonitorProjectInfo
from flaskr.database import db_session

bp = Blueprint('crawler_info', __name__, url_prefix='/crawler_info')


# @bp.route('/query_project_by_id', methods=('GET', 'POST'))
# def query_project_by_id():
#     # todo
#     """
#     根据id查询项目信息
#     :return:
#     """
#     inquire_id = request.args.get('monitor_project_id')
#     print('inquire id={}'.format(inquire_id))
#     page = request.args.get('page')
#     print('page={}'.format(page))
#     # 项目信息为列表
#     project_info = db_session.query(MonitorProjectInfo).filter(MonitorProjectInfo.project_id == inquire_id).all()
#     if not project_info:
#         return jsonify({'success': 'flase', 'error': 'The database does not exist for this project'})
#     else:
#         data_list = []
#         for info_obj in project_info:
#             # 对象转字典并添加到列表中进行反向排序
#             # 上面那行注视是张金肖写的
#             a = info_obj.serialization_info()
#             data_dict = info_obj.__dict__
#             data_dict.pop('_sa_instance_state')
#             print(data_dict)
#             data_list.append(data_dict)
#         # 反向排序,将最新的数据放最前面
#         data_list.reverse()
#         # 分页展示, 每页展示10条数据
#         final_list = []
#         middle_list = []
#         for data in data_list:
#             middle_list.append(data)
#             if len(middle_list) == 10:
#                 pass
#
#
#         json_data = {}
#         json_data['data'] = data_list
#         json_data['success'] = 'true'
#         return jsonify(json_data)


@bp.route('/')
def my_echart():
    return render_template('/crawler_base.html')

@bp.route('/home/', methods=['GET'])
def query_project_list():
    # todo
    """
    查询项目列表
    :return:
    """
    all_project_list = db_session.query(MonitorProject).all()

    if all_project_list is None:
        return jsonify({'success': 'flase', 'error': 'The database does not exist for this project info'})
    else:
        info_list = []
        for project in all_project_list:
            info_list.append(project.serialization_info())
        # return render_template('/crawler_base.html')
        return jsonify([{'xdays': '123',
                         'yvalue': '678'}])


@bp.route('/update_project/', methods=('GET', 'POST'))
def update_project():
    """
    更新项目信息
    :return:
    """
    update_id = request.args.get('monitor_project_info_id')
    total_quantity = request.args.get('total_quantity', type=int, default=None)
    crawler_quantity = request.args.get('crawler_quantity', type=int, default=None)
    result_quantity = request.args.get('result_quantity', type=int, default=None)
    crawler_start_time = request.args.get('crawler_start_time', default=None)
    crawler_end_time = request.args.get('crawler_end_time', default=None)
    author = request.args.get('author', type=str, default=None)
    partner = request.args.get('partner', type=str, default=None)
    # 这里查询条件可以为多个
    project_info = db_session.query(MonitorProjectInfo).filter(MonitorProjectInfo.id == update_id).first()
    if project_info is None:
        return jsonify({'success': 'flase', 'error': 'The database does not exist for this project info'})
    else:
        project_info.total_quantity = total_quantity
        project_info.crawler_quantity = crawler_quantity
        project_info.result_quantity = result_quantity
        project_info.crawler_start_time = crawler_start_time
        project_info.crawler_end_time = crawler_end_time
        project_info.author = author
        project_info.partner = partner
        db_session.commit()
        return jsonify({'success': 'true', 'update_id': update_id})


@bp.route('/delete_project_by_id/', methods=('GET', 'POST'))
def delete_project():
    """
    根据monitor info删除信息

    :return:
    """
    delete_id = request.args.get('monitor_project_info_id')
    print('delete id={}'.format(delete_id))
    m = db_session.query(MonitorProjectInfo).filter(MonitorProjectInfo.id == delete_id).first()
    if m:
        print('result = {}'.format(m))
        db_session.delete(m)
        db_session.commit()
        return jsonify({'success': 'true'})
    else:
        return jsonify({'success': 'false', 'info': '该条数据不存在'})


def insert_project_info(project_id, json_data, project_info):
    project_info.project_id = project_id  # 查询出来

    project_info.total_quantity = json_data['total_quantity']  # 数据总量
    project_info.crawler_quantity = json_data['crawler_quantity']  # 抓取总量
    project_info.result_quantity = json_data['result_quantity']  # 入库总量

    project_info.crawler_start_time = datetime.datetime.now()  # 开始抓取时间
    project_info.crawler_end_time = datetime.datetime.now()  # 结束时间

    project_info.author = json_data['author']  # 作者
    project_info.partner = json_data['partner']  # 协助者

    db_session.add(project_info)
    db_session.commit()


@bp.route('/insert_project/', methods=['POST'])
def insert_project():
    """
    插入一条数据
    {
        "project_name": "ad",
        "total_quantity" : 1,
        "crawler_quantity":1,
        "result_quantity":1,
        "crawler_start_time":1,
        "crawler_end_time":1,
        "author":"小武神",
        "partner":"锦鲤"
    }
    :return:
    """
    json_data = request.get_json()
    project = db_session.query(MonitorProject).filter(MonitorProject.project_name == json_data['project_name']).first()
    print("project={}".format(project))

    if not project:
        # 数据库不存在project id
        m = MonitorProject()
        m.project_name = json_data['project_name']
        db_session.add(m)
        db_session.flush()
        db_session.commit()

        project_info = MonitorProjectInfo()
        insert_project_info(m.id, json_data, project_info)
        print(json_data)
    else:
        # 已经存在，跟新其他信息
        project_info = MonitorProjectInfo()
        insert_project_info(project.id, json_data, project_info)
        print(project.id)

    return jsonify({'success': 'true'})
