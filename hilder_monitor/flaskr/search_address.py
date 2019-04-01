import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from lib.proxy_iterator import Proxies

bp = Blueprint('search_address', __name__, url_prefix='/search_address')
p = Proxies()

search_url = 'https://www.amap.com/service/poiInfo?'


@bp.route('/amap/', methods=['GET'])
def register():
    address = request.args.get('address')
    if not address:
        return jsonify({'success': 'true', 'info': '缺少参数'})
    payload = {
        'query_type': 'TQUERY',
        'pagesize': '30',
        'pagenum': None,
        'qii': 'true',
        'cluster_state': '5',
        'need_utd': 'true',
        'utd_sceneid': '1000',
        'div': 'PC1000',
        'addr_poi_merge': 'true',
        'is_classify': 'true',
        'city': None,
        'keywords': address,
    }
    res = requests.get(search_url, proxies=p.get_one(proxies_number=7), params=payload)
    print(res.json())
    if 'rgv587_flag' in res.json():
        return jsonify({'success': 'false', 'info': '爬虫错误'})
    return jsonify(res.json())
