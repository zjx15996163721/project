# coding=gbk
import aiohttp
import asyncio
import json
import pika
from lib.log import LogHandler
from pymongo import MongoClient
m = MongoClient(host='192.168.0.136', port=27017)
collection_seaweed = m['fangjia']['seaweed']

n = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_city_list = n['fangjiaguanjia']['city_list']
log = LogHandler(__name__)


class GuanJiaProducer:

    def __init__(self):
        self.city_dict = {'台州': 'tz', '嘉兴': 'jx', '宁波': 'nb', '金华': 'jh', '衢州': 'quzhou', '杭州': 'hz', '绍兴': 'sx',
                          '丽水': 'ls', '舟山': 'zs', '湖州': 'huzhou', '温州': 'wz', '哈尔滨': 'hb', '黑河': 'heihe', '七台河': 'qth',
                          '鸡西': 'jixi', '大兴安岭': 'dxal', '佳木斯': 'jms', '大庆': 'dq', '牡丹江': 'mdj', '绥化': 'suihua',
                          '伊春': 'yichun', '双鸭山': 'sys', '齐齐哈尔': 'qq', '鹤岗': 'hegang', '云浮': 'yf', '惠州': 'huizhou',
                          '肇庆': 'zq', '湛江': 'zj', '广州': 'gz', '河源': 'heyuan', '江门': 'jm', '汕尾': 'sw', '深圳': 'sz',
                          '韶关': 'sg', '珠海': 'zh', '梅州': 'mz', '佛山': 'fs', '阳江': 'yj', '潮州': 'chaozhou', '茂名': 'mm',
                          '中山': 'zhongshan', '清远': 'qy', '揭阳': 'jy', '汕头': 'st', '东莞': 'dg', '成都': 'cd', '攀枝花': 'pzh',
                          '甘孜': 'ganzi', '达州': 'dazhou', '凉山': 'liangshan', '阿坝': 'ab', '泸州': 'luzhou', '宜宾': 'yb',
                          '绵阳': 'my', '眉山': 'ms', '南充': 'nanchong', '德阳': 'deyang', '广元': 'guangyuan', '自贡': 'zg',
                          '广安': 'ga', '乐山': 'leshan', '巴中': 'bazhong', '雅安': 'yaan', '遂宁': 'sn', '资阳': 'ziyang',
                          '内江': 'neijiang', '锦州': 'jz', '营口': 'yk', '丹东': 'dd', '本溪': 'bx', '辽阳': 'liaoyang',
                          '铁岭': 'tieling', '葫芦岛': 'hld', '大连': 'dl', '沈阳': 'sy', '盘锦': 'pj', '鞍山': 'as', '抚顺': 'fushun',
                          '朝阳': 'cy', '阜新': 'fx', '梧州': 'wuzhou', '崇左': 'chongzuo', '玉林': 'yulin', '防城港': 'fcg',
                          '钦州': 'qinzhou', '百色': 'baise', '北海': 'bh', '柳州': 'liuzhou', '桂林': 'gl', '贵港': 'gg',
                          '南宁': 'nn', '贺州': 'hezhou', '河池': 'hc', '来宾': 'lb', '池州': 'chizhou', '铜陵': 'tongling',
                          '宿州': 'suzhouah', '芜湖': 'wuhu', '蚌埠': 'bengbu', '阜阳': 'fy', '宣城': 'xuancheng', '六安': 'la',
                          '黄山': 'huangshan', '淮北': 'huaibei', '合肥': 'hf', '淮南': 'hn', '滁州': 'chuzhou', '亳州': 'bozhou',
                          '安庆': 'aq', '马鞍山': 'mas', '邯郸': 'hd', '保定': 'bd', '邢台': 'xt', '承德': 'chengde', '唐山': 'ts',
                          '张家口': 'zjk', '沧州': 'cangzhou', '廊坊': 'lf', '秦皇岛': 'qhd', '衡水': 'hengshui', '石家庄': 'sj',
                          '北京': 'bj', '楚雄': 'cx', '文山': 'ws', '昭通': 'zt', '普洱': 'pe', '大理': 'dali', '迪庆': 'diqing',
                          '德宏': 'dh', '玉溪': 'yx', '保山': 'bs', '西双版纳': 'xsbn', '昆明': 'km', '怒江': 'nujiang',
                          '临沧': 'lincang', '红河': 'honghe', '曲靖': 'qj', '丽江': 'lj', '莱芜': 'lw', '日照': 'rz', '济南': 'jn',
                          '东营': 'dy', '聊城': 'lc', '枣庄': 'zaozhuang', '威海': 'weihai', '潍坊': 'wf', '临沂': 'linyi',
                          '菏泽': 'heze', '青岛': 'qd', '泰安': 'taian', '淄博': 'zb', '济宁': 'jining', '德州': 'dz', '烟台': 'yt',
                          '滨州': 'bz', '鄂州': 'ez', '天门': 'tm', '咸宁': 'xianning', '十堰': 'shiyan', '仙桃': 'xiantao',
                          '荆门': 'jingmen', '随州': 'suizhou', '孝感': 'xg', '襄阳': 'xy', '黄石': 'hs', '宜昌': 'yichang',
                          '神农架': 'snj', '武汉': 'wh', '荆州': 'jingzhou', '潜江': 'qianjiang', '黄冈': 'hg', '恩施': 'es',
                          '南京': 'nj', '宿迁': 'sq', '泰州': 'taizhoujs', '徐州': 'xz', '镇江': 'zhenjiang', '扬州': 'yz',
                          '无锡': 'wx', '盐城': 'yancheng', '常州': 'cz', '苏州': 'su', '连云港': 'lyg', '淮安': 'ha', '南通': 'nt',
                          '焦作': 'jiaozuo', '开封': 'kf', '南阳': 'ny', '洛阳': 'ly', '新乡': 'xinxiang', '安阳': 'ay',
                          '驻马店': 'zmd', '济源': 'jiyuan', '平顶山': 'pds', '商丘': 'shangqiu', '郑州': 'zz', '许昌': 'xc',
                          '濮阳': 'py', '鹤壁': 'hebi', '信阳': 'xinyang', '漯河': 'lh', '周口': 'zk', '三门峡': 'smx', '拉萨': 'lasa',
                          '山南': 'shannan', '阿里': 'al', '日喀则': 'rkz', '林芝': 'linzhi', '昌都': 'changdu', '那曲': 'nq',
                          '西安': 'xa', '宝鸡': 'baoji', '渭南': 'wn', '安康': 'ak', '延安': 'ya', '商洛': 'sl', '铜川': 'tc',
                          '榆林': 'yl', '汉中': 'hanzhong', '咸阳': 'xianyang', '陇南': 'ln', '临夏': 'lx', '甘南': 'gn',
                          '定西': 'dx', '金昌': 'jinchang', '嘉峪关': 'jyg', '庆阳': 'qingyang', '酒泉': 'jq', '兰州': 'lz',
                          '天水': 'tianshui', '白银': 'by', '武威': 'ww', '张掖': 'zhangye', '平凉': 'pl', '邵阳': 'shaoyang',
                          '株洲': 'zhuzhou', '张家界': 'zjj', '怀化': 'huaihua', '湘西': 'xx', '常德': 'changde', '长沙': 'cs',
                          '娄底': 'ld', '永州': 'yongzhou', '衡阳': 'hy', '岳阳': 'yy', '益阳': 'yiyang', '湘潭': 'xiangtan',
                          '郴州': 'chenzhou', '阿克苏': 'aks', '塔城': 'tacheng', '哈密': 'hm', '石河子': 'shz', '铁门关': 'tmg',
                          '伊犁': 'yili', '阿拉尔': 'ale', '博州': 'bozhouxj', '昆玉': 'ky', '五家渠': 'wjq', '和田': 'ht',
                          '阿勒泰': 'alt', '喀什': 'ks', '北屯': 'beitun', '克拉玛依': 'klmy', '昌吉': 'cj', '双河': 'shuanghe',
                          '巴州': 'bazhou', '图木舒克': 'tmsk', '克州': 'kz', '乌鲁木齐': 'wl', '吐鲁番': 'tlf', '可克达拉': 'kkdl',
                          '三明': 'sm', '南平': 'np', '福州': 'fz', '漳州': 'zhangzhou', '龙岩': 'longyan', '泉州': 'qz',
                          '莆田': 'pt', '厦门': 'xm', '宁德': 'nd', '重庆': 'cq', '中卫': 'zw', '银川': 'yc', '固原': 'guyuan',
                          '石嘴山': 'szs', '吴忠': 'wuzhong', '大同': 'dt', '晋城': 'jc', '太原': 'ty', '长治': 'changzhi',
                          '吕梁': 'll', '晋中': 'jinzhong', '忻州': 'xinzhou', '临汾': 'linfen', '阳泉': 'yq', '运城': 'yuncheng',
                          '朔州': 'shuozhou', '黔东南': 'qdn', '铜仁': 'tr', '黔西南': 'qxn', '遵义': 'zy', '六盘水': 'lps',
                          '安顺': 'anshun', '毕节': 'bijie', '贵阳': 'gy', '黔南': 'qn', '锡林郭勒': 'xlgl', '赤峰': 'cf',
                          '乌海': 'wuhai', '兴安': 'xingan', '呼和浩特': 'hh', '巴彦淖尔': 'byne', '阿拉善': 'als', '通辽': 'tl',
                          '乌兰察布': 'wlcb', '呼伦贝尔': 'hlbe', '包头': 'bt', '鄂尔多斯': 'eds', '松原': 'songyuan', '长春': 'cc',
                          '吉林': 'jl', '白山': 'baishan', '辽源': 'liaoyuan', '通化': 'th', '延边': 'yanbian', '四平': 'sp',
                          '白城': 'bc', '上海': 'sh', '天津': 'tj', '果洛': 'guoluo', '黄南': 'huangnan', '海东': 'haidong',
                          '海西': 'hx', '海北': 'haibei', '海南州': 'hnz', '玉树': 'ys', '西宁': 'xn', '临高': 'lg', '三亚': 'sanya',
                          '琼海': 'qh', '儋州': 'danzhou', '乐东': 'ledong', '昌江': 'changjiang', '万宁': 'wanning',
                          '白沙': 'baisha', '陵水': 'lingshui', '文昌': 'wc', '海口': 'hk', '琼中': 'qiongzhong', '五指山': 'wzs',
                          '三沙': 'ss', '定安': 'da', '屯昌': 'tunchang', '保亭': 'baoting', '澄迈': 'cm', '东方': 'df', '萍乡': 'px',
                          '上饶': 'sr', '宜春': 'yichunjx', '吉安': 'ja', '南昌': 'nc', '鹰潭': 'yingtan', '抚州': 'fuzhou',
                          '景德镇': 'jdz', '九江': 'jj', '新余': 'xinyu', '赣州': 'ganzhou'}
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.196', port=5673, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='guanjia')

    def start(self):
        for i in collection_seaweed.find({"status": 0, "cat": "district"}, no_cursor_timeout=True):
            if i['city'] in self.city_dict:
                data = (i['name'], self.city_dict[i['city']])
                self.channel.basic_publish(exchange='',
                                           routing_key='guanjia',
                                           body=json.dumps(data))
                log.info('放队列 {}'.format(data))


if __name__ == '__main__':
    g = GuanJiaProducer()
    g.start()






