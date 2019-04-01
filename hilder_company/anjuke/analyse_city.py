"""
统计城市可以格式化中的有商铺写字楼的个数，以及木有商铺写字楼的个数
统计城市不可以格式化中的有商铺写字楼的个数，以及木有商铺写字楼的个数
"""

can_not_stan_city = [{'澳门': 'https://aomen.anjuke.com'}, {'安达': 'https://anda.anjuke.com'},
                     {'安丘': 'https://anqiu.anjuke.com'}, {'安宁': 'https://anning.anjuke.com'},
                     {'安国': 'https://anguo.anjuke.com'}, {'阿尔山': 'https://aershan.anjuke.com'},
                     {'阿图什': 'https://atushi.anjuke.com'}, {'安陆': 'https://anlu.anjuke.com'},
                     {'霸州': 'https://bazh.anjuke.com'}, {'北安': 'https://beian.anjuke.com'},
                     {'北票': 'https://beipiao.anjuke.com'}, {'泊头': 'https://botou.anjuke.com'},
                     {'博乐': 'https://bole.anjuke.com'}, {'北流': 'https://beiliu.anjuke.com'},
                     {'巢湖': 'https://chaohu.anjuke.com'}, {'长葛': 'https://changge.anjuke.com'},
                     {'常熟': 'https://changshushi.anjuke.com'}, {'昌邑': 'https://changyi.anjuke.com'},
                     {'常宁': 'https://changning.anjuke.com'}, {'赤壁': 'https://chibi.anjuke.com'},
                     {'岑溪': 'https://cengxi.anjuke.com'}, {'赤水': 'https://chishui.anjuke.com'},
                     {'慈溪': 'https://cixi.anjuke.com'}, {'大丰': 'https://dafeng.anjuke.com'},
                     {'定州': 'https://dingzhou.anjuke.com'}, {'东台': 'https://dongtai.anjuke.com'},
                     {'邓州': 'https://dengzhou.anjuke.com'}, {'德惠': 'https://dehui.anjuke.com'},
                     {'当阳': 'https://dangyang.anjuke.com'}, {'敦化': 'https://dunhuashi.anjuke.com'},
                     {'丹阳': 'https://danyang.anjuke.com'}, {'大石桥': 'https://dashiqiao.anjuke.com'},
                     {'灯塔': 'https://dengta.anjuke.com'}, {'敦煌': 'https://dunhuang.anjuke.com'},
                     {'德令哈': 'https://delingha.anjuke.com'}, {'大冶': 'https://daye.anjuke.com'},
                     {'都匀': 'https://duyun.anjuke.com'}, {'东兴': 'https://dongxing.anjuke.com'},
                     {'东阳': 'https://dongyang.anjuke.com'}, {'德兴': 'https://dexing.anjuke.com'},
                     {'丹江口': 'https://danjiangkou.anjuke.com'}, {'都江堰': 'https://dujiangyan.anjuke.com'},
                     {'东港': 'https://donggang.anjuke.com'}, {'登封': 'https://dengfeng.anjuke.com'},
                     {'恩平': 'https://enping.anjuke.com'}, {'肥城': 'https://feichengshi.anjuke.com'},
                     {'丰城': 'https://fengchengshi.anjuke.com'}, {'丰镇': 'https://fengzhen.anjuke.com'},
                     {'汾阳': 'https://fenyang.anjuke.com'}, {'阜康': 'https://fukang.anjuke.com'},
                     {'福泉': 'https://fuquan.anjuke.com'}, {'福清': 'https://fuqing.anjuke.com'},
                     {'福安': 'https://fuan.anjuke.com'}, {'凤城': 'https://fengcheng.anjuke.com'},
                     {'福鼎': 'https://fuding.anjuke.com'}, {'甘孜': 'https://ganzi.anjuke.com'},
                     {'馆陶': 'https://guantao.anjuke.com'}, {'公主岭': 'https://gongzhulingshi.anjuke.com'},
                     {'高邮': 'https://gaoyou.anjuke.com'}, {'高密': 'https://gaomishi.anjuke.com'},
                     {'广水': 'https://guangshui.anjuke.com'}, {'格尔木': 'https://geermu.anjuke.com'},
                     {'广汉': 'https://guanghan.anjuke.com'}, {'个旧': 'https://gejiu.anjuke.com'},
                     {'桂平': 'https://guiping.anjuke.com'}, {'贵溪': 'https://guixi.anjuke.com'},
                     {'高安': 'https://gaoanshi.anjuke.com'}, {'高州': 'https://gaozhou.anjuke.com'},
                     {'高要': 'https://gaoyaoshi.anjuke.com'}, {'古交': 'https://gujiao.anjuke.com'},
                     {'高碑店': 'https://gaobeidian.anjuke.com'}, {'海南': 'https://hainan.anjuke.com'},
                     {'和县': 'https://hexian.anjuke.com'}, {'海拉尔': 'https://hailaer.anjuke.com'},
                     {'霍邱': 'https://huoqiu.anjuke.com'}, {'桦甸': 'https://huadian.anjuke.com'},
                     {'鹤山': 'https://heshan.anjuke.com'}, {'海林': 'https://hailin.anjuke.com'},
                     {'海城': 'https://haicheng.anjuke.com'}, {'珲春': 'https://hunchun.anjuke.com'},
                     {'黄骅': 'https://huanghua.anjuke.com'}, {'河间': 'https://hejian.anjuke.com'},
                     {'韩城': 'https://hancheng.anjuke.com'}, {'华阴': 'https://huaying.anjuke.com'},
                     {'侯马': 'https://houma.anjuke.com'}, {'汉川': 'https://hanchuan.anjuke.com'},
                     {'华蓥': 'https://huaying2.anjuke.com'}, {'合山': 'https://heshanshi.anjuke.com'},
                     {'辉县': 'https://huixian.anjuke.com'}, {'化州': 'https://huazhou.anjuke.com'},
                     {'霍州': 'https://huozhou.anjuke.com'}, {'洪湖': 'https://honghu.anjuke.com'},
                     {'洪江': 'https://hongjiang.anjuke.com'}, {'和龙': 'https://helong.anjuke.com'},
                     {'海门': 'https://haimen.anjuke.com'}, {'海宁': 'https://haining.anjuke.com'},
                     {'江阴': 'https://jiangyin.anjuke.com'}, {'靖江': 'https://jingjiang.anjuke.com'},
                     {'简阳': 'https://jianyangshi.anjuke.com'}, {'金坛': 'https://jintan.anjuke.com'},
                     {'津市': 'https://jinshi.anjuke.com'}, {'界首': 'https://jieshou.anjuke.com'},
                     {'吉首': 'https://jishou.anjuke.com'}, {'景洪': 'https://jinghong.anjuke.com'},
                     {'晋江': 'https://jinjiangshi.anjuke.com'}, {'建瓯': 'https://jianou.anjuke.com'},
                     {'江山': 'https://jiangshan.anjuke.com'}, {'井冈山': 'https://jinggangshan.anjuke.com'},
                     {'蛟河': 'https://jiaohe.anjuke.com'}, {'胶州': 'https://jiaozhoux.anjuke.com'},
                     {'句容': 'https://jurong.anjuke.com'}, {'建德': 'https://jiande.anjuke.com'},
                     {'冀州': 'https://jizhoushi.anjuke.com'}, {'江油市': 'https://jiangyoushi.anjuke.com'},
                     {'昆山': 'https://ks.anjuke.com'}, {'垦利': 'https://kenli.anjuke.com'},
                     {'库尔勒': 'https://kuerle.anjuke.com'}, {'奎屯': 'https://kuitun.anjuke.com'},
                     {'凯里': 'https://kaili.anjuke.com'}, {'开平': 'https://kaiping.anjuke.com'},
                     {'开原': 'https://kaiyuan.anjuke.com'}, {'开远': 'https://kaiyuan2.anjuke.com'},
                     {'临猗': 'https://linyishi.anjuke.com'}, {'临海': 'https://linhaishi.anjuke.com'},
                     {'龙海': 'https://longhaishi.anjuke.com'}, {'醴陵': 'https://lilingshi.anjuke.com'},
                     {'临清': 'https://linqing.anjuke.com'}, {'龙口': 'https://longkou.anjuke.com'},
                     {'莱阳': 'https://laiyang.anjuke.com'}, {'耒阳': 'https://leiyang.anjuke.com'},
                     {'溧阳': 'https://liyang.anjuke.com'}, {'龙井': 'https://longjing.anjuke.com'},
                     {'临江': 'https://linjiang.anjuke.com'}, {'凌源': 'https://lingyuan.anjuke.com'},
                     {'林州': 'https://linzhoushi.anjuke.com'}, {'灵宝': 'https://lingbao.anjuke.com'},
                     {'潞城': 'https://lucheng.anjuke.com'}, {'利川': 'https://lichuan.anjuke.com'},
                     {'冷水江': 'https://lengshuijiang.anjuke.com'}, {'涟源': 'https://lianyuan.anjuke.com'},
                     {'阆中': 'https://langzhong.anjuke.com'}, {'潞西': 'https://luxishi.anjuke.com'},
                     {'兰溪': 'https://lanxi.anjuke.com'}, {'乐昌': 'https://lechang.anjuke.com'},
                     {'廉江': 'https://lianjiangshi.anjuke.com'}, {'雷州': 'https://leizhou.anjuke.com'},
                     {'陆丰': 'https://lufengshi.anjuke.com'}, {'连州': 'https://lianzhou.anjuke.com'},
                     {'罗定': 'https://luoding.anjuke.com'}, {'临湘': 'https://linxiang.anjuke.com'},
                     {'龙泉': 'https://longquan.anjuke.com'}, {'乐平': 'https://leping.anjuke.com'},
                     {'乐陵': 'https://laoling.anjuke.com'}, {'莱州': 'https://laizhoushi.anjuke.com'},
                     {'浏阳': 'https://liuyang.anjuke.com'}, {'老河口': 'https://laohekou.anjuke.com'},
                     {'莱西': 'https://laixi.anjuke.com'}, {'明港': 'https://minggang.anjuke.com'},
                     {'密山': 'https://mishan.anjuke.com'}, {'梅河口': 'https://meihekou.anjuke.com'},
                     {'满洲里': 'https://manzhouli.anjuke.com'}, {'孟州': 'https://mengzhou.anjuke.com'},
                     {'麻城': 'https://macheng.anjuke.com'}, {'绵竹': 'https://mianzhu.anjuke.com'},
                     {'明光': 'https://mingguang.anjuke.com'}, {'汨罗': 'https://miluo.anjuke.com'},
                     {'南安': 'https://nananshi.anjuke.com'}, {'宁安': 'https://ninganshi.anjuke.com'},
                     {'宁国': 'https://ningguo.anjuke.com'}, {'南康': 'https://nankang.anjuke.com'},
                     {'南雄': 'https://nanxiong.anjuke.com'}, {'讷河': 'https://nehe.anjuke.com'},
                     {'南宫': 'https://nangong.anjuke.com'}, {'普宁': 'https://puning.anjuke.com'},
                     {'普兰店': 'https://pulandian.anjuke.com'}, {'凭祥': 'https://pingxiangshi.anjuke.com'},
                     {'邳州': 'https://pizhou.anjuke.com'}, {'蓬莱': 'https://penglaishi.anjuke.com'},
                     {'平湖': 'https://pinghu.anjuke.com'}, {'平度': 'https://pingdu.anjuke.com'},
                     {'彭州': 'https://pengzhou.anjuke.com'}, {'清徐': 'https://qingxu.anjuke.com'},
                     {'迁安': 'https://qiananshi.anjuke.com'}, {'青州': 'https://qingzhoushi.anjuke.com'},
                     {'清镇': 'https://qingzhen.anjuke.com'}, {'青铜峡': 'https://qingtongxia.anjuke.com'},
                     {'沁阳': 'https://qinyangshi.anjuke.com'}, {'曲阜': 'https://qufu.anjuke.com'},
                     {'邛崃': 'https://qionglai.anjuke.com'}, {'启东': 'https://qidong.anjuke.com'},
                     {'瑞安': 'https://ruian.anjuke.com'}, {'汝州': 'https://ruzhoushi.anjuke.com'},
                     {'任丘': 'https://renqiushi.anjuke.com'}, {'瑞金': 'https://ruijin.anjuke.com'},
                     {'乳山': 'https://rushan.anjuke.com'}, {'仁怀': 'https://renhuai.anjuke.com'},
                     {'瑞昌': 'https://ruichang.anjuke.com'}, {'瑞丽': 'https://ruili.anjuke.com'},
                     {'如皋': 'https://rugao.anjuke.com'}, {'荣成市': 'https://rongchengshi.anjuke.com'},
                     {'顺德': 'https://shunde.anjuke.com'}, {'沭阳': 'https://shuyang.anjuke.com'},
                     {'石狮': 'https://shishi.anjuke.com'}, {'三河': 'https://sanheshi.anjuke.com'},
                     {'尚志': 'https://shangzhi.anjuke.com'}, {'寿光': 'https://shouguang.anjuke.com'},
                     {'嵊州': 'https://shengzhou.anjuke.com'}, {'绥芬河': 'https://suifenhe.anjuke.com'},
                     {'什邡': 'https://shifang.anjuke.com'}, {'四会': 'https://sihui.anjuke.com'},
                     {'邵武': 'https://shaowu.anjuke.com'}, {'松滋': 'https://songzi.anjuke.com'},
                     {'石首': 'https://shishou.anjuke.com'}, {'韶山': 'https://shaoshan.anjuke.com'},
                     {'深州': 'https://shenzhou.anjuke.com'}, {'沙河': 'https://shahe.anjuke.com'},
                     {'台山': 'https://taishan.anjuke.com'}, {'桐城': 'https://tongcheng.anjuke.com'},
                     {'台湾': 'https://taiwan.anjuke.com'}, {'太仓': 'https://taicang.anjuke.com'},
                     {'泰兴': 'https://taixing.anjuke.com'}, {'滕州': 'https://tengzhoushi.anjuke.com'},
                     {'洮南': 'https://taonan.anjuke.com'}, {'铁力': 'https://tieli.anjuke.com'},
                     {'桐乡': 'https://tongxiang.anjuke.com'}, {'天长': 'https://tianchang.anjuke.com'},
                     {'文山': 'https://wenshan.anjuke.com'}, {'瓦房店': 'https://wafangdian.anjuke.com'},
                     {'武夷山': 'https://wuyishan.anjuke.com'}, {'温岭': 'https://wnelingshi.anjuke.com'},
                     {'武安': 'https://wuanshi.anjuke.com'}, {'舞钢': 'https://wugang.anjuke.com'},
                     {'五常': 'https://wuchang.anjuke.com'}, {'卫辉': 'https://weihui.anjuke.com'},
                     {'武冈': 'https://wugangshi.anjuke.com'}, {'乌兰浩特': 'https://wulanhaote.anjuke.com'},
                     {'武穴': 'https://wuxue.anjuke.com'}, {'万源': 'https://wanyuan.anjuke.com'},
                     {'吴川': 'https://wuchuan.anjuke.com'}, {'香港': 'https://xianggang.anjuke.com'},
                     {'新泰': 'https://xintaishi.anjuke.com'}, {'新乐': 'https://xinle.anjuke.com'},
                     {'湘乡': 'https://xiangxiang.anjuke.com'}, {'锡林浩特': 'https://xilinhaote.anjuke.com'},
                     {'辛集': 'https://xinji.anjuke.com'}, {'新民': 'https://xinmin.anjuke.com'},
                     {'兴平': 'https://xingping.anjuke.com'}, {'兴义': 'https://xingyi.anjuke.com'},
                     {'宣威': 'https://xuanwei.anjuke.com'}, {'兴宁': 'https://xingning.anjuke.com'},
                     {'项城': 'https://xiangcheng.anjuke.com'}, {'信宜': 'https://xinyi.anjuke.com'},
                     {'孝义': 'https://xiaoyi.anjuke.com'}, {'兴城': 'https://xingcheng.anjuke.com'},
                     {'新沂': 'https://xinyishi.anjuke.com'}, {'荥阳': 'https://xingyang.anjuke.com'},
                     {'新郑': 'https://xinzheng.anjuke.com'}, {'新密': 'https://xinmi.anjuke.com'},
                     {'义乌': 'https://yiwu.anjuke.com'}, {'阳春': 'https://yangchun.anjuke.com'},
                     {'鄢陵': 'https://yanling.anjuke.com'}, {'玉树': 'https://yushu.anjuke.com'},
                     {'乐清': 'https://yueqing.anjuke.com'}, {'禹州': 'https://yuzhou.anjuke.com'},
                     {'永新': 'https://yongxin.anjuke.com'}, {'永康': 'https://yongkangshi.anjuke.com'},
                     {'榆树': 'https://yushushi.anjuke.com'}, {'永安': 'https://yongan.anjuke.com'},
                     {'宜都': 'https://yidou.anjuke.com'}, {'仪征': 'https://yizheng.anjuke.com'},
                     {'延吉': 'https://yanji.anjuke.com'}, {'扬中': 'https://yangzhong.anjuke.com'},
                     {'牙克石': 'https://yakeshi.anjuke.com'}, {'伊宁': 'https://yining.anjuke.com'},
                     {'永济': 'https://yongji.anjuke.com'}, {'应城': 'https://yingchengshi.anjuke.com'},
                     {'宜州': 'https://yizhou.anjuke.com'}, {'英德': 'https://yingde.anjuke.com'},
                     {'玉门': 'https://yumen.anjuke.com'}, {'禹城': 'https://yucheng.anjuke.com'},
                     {'余姚': 'https://yuyao.anjuke.com'}, {'偃师': 'https://yanshishi.anjuke.com'},
                     {'永城': 'https://yongcheng.anjuke.com'}, {'宜兴': 'https://yixing.anjuke.com'},
                     {'沅江': 'https://yuanjiang.anjuke.com'}, {'章丘': 'https://zhangqiu.anjuke.com'},
                     {'诸城': 'https://zhucheng.anjuke.com'}, {'庄河': 'https://zhuanghe.anjuke.com'},
                     {'正定': 'https://zhengding.anjuke.com'}, {'张北': 'https://zhangbei.anjuke.com'},
                     {'赵县': 'https://zhaoxian.anjuke.com'}, {'邹城': 'https://zouchengshi.anjuke.com'},
                     {'遵化': 'https://zunhua.anjuke.com'}, {'肇东': 'https://zhaodong.anjuke.com'},
                     {'张家港': 'https://zhangjiagang.anjuke.com'}, {'枝江': 'https://zhijiang.anjuke.com'},
                     {'招远': 'https://zhaoyuanshi.anjuke.com'}, {'钟祥': 'https://zhongxiang.anjuke.com'},
                     {'资兴': 'https://zixing.anjuke.com'}, {'樟树': 'https://zhangshu.anjuke.com'},
                     {'扎兰屯': 'https://zhalandun.anjuke.com'}, {'诸暨': 'https://zhuji.anjuke.com'},
                     {'涿州': 'https://zhuozhoushi.anjuke.com'}, {'枣阳': 'https://zaoyangshi.anjuke.com'},
                     {'漳平': 'https://zhangping.anjuke.com'}, {'大邑': 'https://chengdu.anjuke.com'},
                     {'金堂': 'https://chengdu.anjuke.com'}, {'栖霞': 'https://nanjing.anjuke.com'},
                     {'淳安': 'https://hangzhou.anjuke.com'}, {'富阳': 'https://hangzhou.anjuke.com'},
                     {'桐庐': 'https://hangzhou.anjuke.com'}, {'铜梁': 'https://chongqing.anjuke.com'},
                     {'丰都': 'https://chongqing.anjuke.com'}, {'长寿': 'https://chongqing.anjuke.com'},
                     {'涪陵': 'https://chongqing.anjuke.com'}, {'南川': 'https://chongqing.anjuke.com'},
                     {'永川': 'https://chongqing.anjuke.com'}, {'綦江': 'https://chongqing.anjuke.com'},
                     {'黔江': 'https://chongqing.anjuke.com'}, {'江津': 'https://chongqing.anjuke.com'},
                     {'合川': 'https://chongqing.anjuke.com'}, {'普兰店': 'https://dalian.anjuke.com'},
                     {'平阴': 'https://jinan.anjuke.com'}, {'济阳': 'https://jinan.anjuke.com'},
                     {'商河': 'https://jinan.anjuke.com'}, {'中牟': 'https://zhengzhou.anjuke.com'},
                     {'巩义': 'https://zhengzhou.anjuke.com'}, {'宁乡': 'https://cs.anjuke.com'},
                     {'无极': 'https://sjz.anjuke.com'}, {'辛集': 'https://sjz.anjuke.com'},
                     {'元氏': 'https://sjz.anjuke.com'}, {'即墨': 'https://qd.anjuke.com'}, {'胶南': 'https://qd.anjuke.com'},
                     {'周至': 'https://xa.anjuke.com'}, {'户县': 'https://xa.anjuke.com'}, {'蓝田': 'https://xa.anjuke.com'},
                     {'宁海': 'https://nb.anjuke.com'}, {'象山': 'https://nb.anjuke.com'}, {'肥东': 'https://hf.anjuke.com'},
                     {'肥西': 'https://hf.anjuke.com'}, {'庐江': 'https://hf.anjuke.com'}, {'长丰': 'https://hf.anjuke.com'},
                     {'长乐': 'https://fz.anjuke.com'}, {'连江': 'https://fz.anjuke.com'}, {'平潭': 'https://fz.anjuke.com'},
                     {'安宁': 'https://km.anjuke.com'}, {'宜良': 'https://km.anjuke.com'}, {'清镇': 'https://gy.anjuke.com'},
                     {'辽中': 'https://sy.anjuke.com'}, {'新民': 'https://sy.anjuke.com'}, {'进贤': 'https://nc.anjuke.com'},
                     {'新建': 'https://nc.anjuke.com'}, {'溧阳': 'https://cz.anjuke.com'}, {'嘉善': 'https://jx.anjuke.com'},
                     {'莱阳': 'https://yt.anjuke.com'}, {'龙口': 'https://yt.anjuke.com'}, {'招远': 'https://yt.anjuke.com'},
                     {'农安': 'https://cc.anjuke.com'}, {'博罗': 'https://huizhou.anjuke.com'},
                     {'惠东': 'https://huizhou.anjuke.com'}, {'龙门': 'https://huizhou.anjuke.com'},
                     {'昌邑': 'https://jilin.anjuke.com'}, {'永登': 'https://lanzhou.anjuke.com'},
                     {'榆中': 'https://lanzhou.anjuke.com'}, {'文安': 'https://langfang.anjuke.com'},
                     {'孟津': 'https://luoyang.anjuke.com'}, {'汝阳': 'https://luoyang.anjuke.com'},
                     {'新安': 'https://luoyang.anjuke.com'}, {'伊川': 'https://luoyang.anjuke.com'},
                     {'宜阳': 'https://luoyang.anjuke.com'}, {'宾阳': 'https://nanning.anjuke.com'},
                     {'横县': 'https://nanning.anjuke.com'}, {'海安': 'https://nantong.anjuke.com'},
                     {'启东': 'https://nantong.anjuke.com'}, {'如东': 'https://nantong.anjuke.com'},
                     {'安溪': 'https://quanzhou.anjuke.com'}, {'惠安': 'https://quanzhou.anjuke.com'},
                     {'永春': 'https://quanzhou.anjuke.com'}, {'晋安': 'https://quanzhou.anjuke.com'},
                     {'上虞': 'https://shaoxing.anjuke.com'}, {'乐亭': 'https://tangshan.anjuke.com'},
                     {'滦南': 'https://tangshan.anjuke.com'}, {'滦县': 'https://tangshan.anjuke.com'},
                     {'迁西': 'https://tangshan.anjuke.com'}, {'玉田': 'https://tangshan.anjuke.com'},
                     {'安丘': 'https://weifang.anjuke.com'}, {'昌乐': 'https://weifang.anjuke.com'},
                     {'高密': 'https://weifang.anjuke.com'}, {'青州': 'https://weifang.anjuke.com'},
                     {'寿光': 'https://weifang.anjuke.com'}, {'丰县': 'https://xuzhou.anjuke.com'},
                     {'沛县': 'https://xuzhou.anjuke.com'}, {'睢宁': 'https://xuzhou.anjuke.com'},
                     {'宝应': 'https://yangzhou.anjuke.com'}, {'高邮': 'https://yangzhou.anjuke.com'},
                     {'仪征': 'https://yangzhou.anjuke.com'}, {'当阳': 'https://yichang.anjuke.com'},
                     {'宜都': 'https://yichang.anjuke.com'}, {'枝江': 'https://yichang.anjuke.com'},
                     {'丹阳市': 'https://zhenjiang.anjuke.com'}, {'扬中市': 'https://zhenjiang.anjuke.com'},
                     {'邹平': 'https://binzhou.anjuke.com'}, {'广饶': 'https://dongying.anjuke.com'},
                     {'玉环': 'https://taiz.anjuke.com'}, {'肇源': 'https://daqing.anjuke.com'},
                     {'东海': 'https://lianyungang.anjuke.com'}, {'德清': 'https://huzhou.anjuke.com'},
                     {'长兴': 'https://huzhou.anjuke.com'}, {'建湖': 'https://yancheng.anjuke.com'},
                     {'当涂': 'https://maanshan.anjuke.com'}, {'宁国': 'https://xuancheng.anjuke.com'}]


city_list = [{'鞍山': 'https://anshan.anjuke.com'}, {'安阳': 'https://anyang.anjuke.com'},
             {'安庆': 'https://anqing.anjuke.com'}, {'安康': 'https://ankang.anjuke.com'},
             {'安顺': 'https://anshun.anjuke.com'}, {'阿坝': 'https://aba.anjuke.com'}, {'阿克苏': 'https://akesu.anjuke.com'},
             {'阿里': 'https://ali.anjuke.com'}, {'阿拉尔': 'https://alaer.anjuke.com'},
             {'阿拉善盟': 'https://alashanmeng.anjuke.com'}, {'北京': 'https://beijing.anjuke.com'},
             {'保定': 'https://baoding.anjuke.com'}, {'包头': 'https://baotou.anjuke.com'},
             {'滨州': 'https://binzhou.anjuke.com'}, {'宝鸡': 'https://baoji.anjuke.com'},
             {'蚌埠': 'https://bengbu.anjuke.com'}, {'本溪': 'https://benxi.anjuke.com'},
             {'北海': 'https://beihai.anjuke.com'}, {'巴音郭楞': 'https://bayinguoleng.anjuke.com'},
             {'巴中': 'https://bazhong.anjuke.com'}, {'巴彦淖尔市': 'https://bayannaoer.anjuke.com'},
             {'亳州': 'https://bozhou.anjuke.com'}, {'白银': 'https://baiyin.anjuke.com'},
             {'白城': 'https://baicheng.anjuke.com'}, {'百色': 'https://baise.anjuke.com'},
             {'白山': 'https://baishan.anjuke.com'}, {'博尔塔拉': 'https://boertala.anjuke.com'},
             {'毕节': 'https://bijie.anjuke.com'}, {'保山': 'https://baoshan.anjuke.com'},
             {'成都': 'https://chengdu.anjuke.com'}, {'重庆': 'https://chongqing.anjuke.com'},
             {'长沙': 'https://cs.anjuke.com'}, {'常州': 'https://cz.anjuke.com'}, {'长春': 'https://cc.anjuke.com'},
             {'沧州': 'https://cangzhou.anjuke.com'}, {'昌吉': 'https://changji.anjuke.com'},
             {'赤峰': 'https://chifeng.anjuke.com'}, {'常德': 'https://changde.anjuke.com'},
             {'郴州': 'https://chenzhou.anjuke.com'}, {'承德': 'https://chengde.anjuke.com'},
             {'长治': 'https://changzhi.anjuke.com'}, {'池州': 'https://chizhou.anjuke.com'},
             {'滁州': 'https://chuzhou.anjuke.com'}, {'朝阳': 'https://chaoyang.anjuke.com'},
             {'潮州': 'https://chaozhou.anjuke.com'}, {'楚雄': 'https://chuxiong.anjuke.com'},
             {'昌都': 'https://changdu.anjuke.com'}, {'崇左': 'https://chongzuo.anjuke.com'},
             {'崇州': 'https://chongzhou.anjuke.com'}, {'大连': 'https://dalian.anjuke.com'},
             {'东莞': 'https://dg.anjuke.com'}, {'德阳': 'https://deyang.anjuke.com'}, {'大理': 'https://dali.anjuke.com'},
             {'德州': 'https://dezhou.anjuke.com'}, {'东营': 'https://dongying.anjuke.com'},
             {'大庆': 'https://daqing.anjuke.com'}, {'丹东': 'https://dandong.anjuke.com'},
             {'大同': 'https://datong.anjuke.com'}, {'达州': 'https://dazhou.anjuke.com'},
             {'德宏': 'https://dehong.anjuke.com'}, {'迪庆': 'https://diqing.anjuke.com'},
             {'定西': 'https://dingxi.anjuke.com'}, {'大兴安岭': 'https://dxanling.anjuke.com'},
             {'东方': 'https://dongfang.anjuke.com'}, {'儋州': 'https://danzhou.anjuke.com'},
             {'鄂尔多斯': 'https://eerduosi.anjuke.com'}, {'恩施': 'https://enshi.anjuke.com'},
             {'鄂州': 'https://ezhou.anjuke.com'}, {'峨眉山': 'https://emeishan.anjuke.com'},
             {'佛山': 'https://foshan.anjuke.com'}, {'福州': 'https://fz.anjuke.com'}, {'阜阳': 'https://fuyang.anjuke.com'},
             {'抚顺': 'https://fushun.anjuke.com'}, {'阜新': 'https://fuxin.anjuke.com'},
             {'抚州': 'https://fuzhoushi.anjuke.com'}, {'防城港': 'https://fangchenggang.anjuke.com'},
             {'广州': 'https://guangzhou.anjuke.com'}, {'贵阳': 'https://gy.anjuke.com'},
             {'桂林': 'https://guilin.anjuke.com'}, {'赣州': 'https://ganzhou.anjuke.com'},
             {'广安': 'https://guangan.anjuke.com'}, {'贵港': 'https://guigang.anjuke.com'},
             {'广元': 'https://guangyuan.anjuke.com'}, {'甘南': 'https://gannan.anjuke.com'},
             {'果洛': 'https://guoluo.anjuke.com'}, {'固原': 'https://guyuan.anjuke.com'},
             {'盖州': 'https://gaizhou.anjuke.com'}, {'杭州': 'https://hangzhou.anjuke.com'},
             {'合肥': 'https://hf.anjuke.com'}, {'哈尔滨': 'https://heb.anjuke.com'}, {'海口': 'https://haikou.anjuke.com'},
             {'惠州': 'https://huizhou.anjuke.com'}, {'邯郸': 'https://handan.anjuke.com'},
             {'呼和浩特': 'https://huhehaote.anjuke.com'}, {'黄冈': 'https://huanggang.anjuke.com'},
             {'淮南': 'https://huainan.anjuke.com'}, {'黄山': 'https://huangshan.anjuke.com'},
             {'鹤壁': 'https://hebi.anjuke.com'}, {'衡阳': 'https://hengyang.anjuke.com'},
             {'湖州': 'https://huzhou.anjuke.com'}, {'衡水': 'https://hengshui.anjuke.com'},
             {'汉中': 'https://hanzhong.anjuke.com'}, {'淮安': 'https://huaian.anjuke.com'},
             {'黄石': 'https://huangshi.anjuke.com'}, {'菏泽': 'https://heze.anjuke.com'},
             {'怀化': 'https://huaihua.anjuke.com'}, {'淮北': 'https://huaibei.anjuke.com'},
             {'葫芦岛': 'https://huludao.anjuke.com'}, {'河源': 'https://heyuan.anjuke.com'},
             {'红河': 'https://honghe.anjuke.com'}, {'哈密': 'https://hami.anjuke.com'},
             {'鹤岗': 'https://hegang.anjuke.com'}, {'呼伦贝尔': 'https://hulunbeier.anjuke.com'},
             {'海北': 'https://haibei.anjuke.com'}, {'海东': 'https://haidong.anjuke.com'},
             {'河池': 'https://hechi.anjuke.com'}, {'黑河': 'https://heihe.anjuke.com'},
             {'贺州': 'https://hezhou.anjuke.com'}, {'和田': 'https://hetian.anjuke.com'},
             {'黄南': 'https://huangnan.anjuke.com'}, {'海西': 'https://hexi.anjuke.com'},
             {'海阳': 'https://haiyang.anjuke.com'}, {'济南': 'https://jinan.anjuke.com'}, {'嘉兴': 'https://jx.anjuke.com'},
             {'吉林': 'https://jilin.anjuke.com'}, {'江门': 'https://jiangmen.anjuke.com'},
             {'荆门': 'https://jingmen.anjuke.com'}, {'锦州': 'https://jinzhou.anjuke.com'},
             {'景德镇': 'https://jingdezhen.anjuke.com'}, {'吉安': 'https://jian.anjuke.com'},
             {'济宁': 'https://jining.anjuke.com'}, {'金华': 'https://jinhua.anjuke.com'},
             {'揭阳': 'https://jieyang.anjuke.com'}, {'晋中': 'https://jinzhong.anjuke.com'},
             {'九江': 'https://jiujiang.anjuke.com'}, {'焦作': 'https://jiaozuo.anjuke.com'},
             {'晋城': 'https://jincheng.anjuke.com'}, {'荆州': 'https://jingzhou.anjuke.com'},
             {'佳木斯': 'https://jiamusi.anjuke.com'}, {'酒泉': 'https://jiuquan.anjuke.com'},
             {'鸡西': 'https://jixi.anjuke.com'}, {'济源': 'https://jiyuan.anjuke.com'},
             {'金昌': 'https://jinchang.anjuke.com'}, {'嘉峪关': 'https://jiayuguan.anjuke.com'},
             {'昆明': 'https://km.anjuke.com'}, {'开封': 'https://kaifeng.anjuke.com'}, {'喀什': 'https://kashi.anjuke.com'},
             {'克拉玛依': 'https://kelamayi.anjuke.com'}, {'克孜勒苏': 'https://lezilesu.anjuke.com'},
             {'兰州': 'https://lanzhou.anjuke.com'}, {'廊坊': 'https://langfang.anjuke.com'},
             {'洛阳': 'https://luoyang.anjuke.com'}, {'柳州': 'https://liuzhou.anjuke.com'},
             {'莱芜': 'https://laiwu.anjuke.com'}, {'六安': 'https://luan.anjuke.com'}, {'泸州': 'https://luzhou.anjuke.com'},
             {'丽江': 'https://lijiang.anjuke.com'}, {'临沂': 'https://linyi.anjuke.com'},
             {'聊城': 'https://liaocheng.anjuke.com'}, {'连云港': 'https://lianyungang.anjuke.com'},
             {'丽水': 'https://lishui.anjuke.com'}, {'娄底': 'https://loudi.anjuke.com'},
             {'乐山': 'https://leshan.anjuke.com'}, {'辽阳': 'https://liaoyang.anjuke.com'},
             {'拉萨': 'https://lasa.anjuke.com'}, {'临汾': 'https://linfen.anjuke.com'},
             {'龙岩': 'https://longyan.anjuke.com'}, {'漯河': 'https://luohe.anjuke.com'},
             {'凉山': 'https://liangshan.anjuke.com'}, {'六盘水': 'https://liupanshui.anjuke.com'},
             {'辽源': 'https://liaoyuan.anjuke.com'}, {'来宾': 'https://laibin.anjuke.com'},
             {'临沧': 'https://lingcang.anjuke.com'}, {'临夏': 'https://linxia.anjuke.com'},
             {'林芝': 'https://linzhi.anjuke.com'}, {'陇南': 'https://longnan.anjuke.com'},
             {'吕梁': 'https://lvliang.anjuke.com'}, {'绵阳': 'https://mianyang.anjuke.com'},
             {'茂名': 'https://maoming.anjuke.com'}, {'马鞍山': 'https://maanshan.anjuke.com'},
             {'牡丹江': 'https://mudanjiang.anjuke.com'}, {'眉山': 'https://meishan.anjuke.com'},
             {'梅州': 'https://meizhou.anjuke.com'}, {'南京': 'https://nanjing.anjuke.com'},
             {'宁波': 'https://nb.anjuke.com'}, {'南昌': 'https://nc.anjuke.com'}, {'南宁': 'https://nanning.anjuke.com'},
             {'南通': 'https://nantong.anjuke.com'}, {'南充': 'https://nanchong.anjuke.com'},
             {'南阳': 'https://nanyang.anjuke.com'}, {'宁德': 'https://ningde.anjuke.com'},
             {'内江': 'https://neijiang.anjuke.com'}, {'南平': 'https://nanping.anjuke.com'},
             {'那曲': 'https://naqu.anjuke.com'}, {'怒江': 'https://nujiang.anjuke.com'},
             {'攀枝花': 'https://panzhihua.anjuke.com'}, {'平顶山': 'https://pingdingsha.anjuke.com'},
             {'盘锦': 'https://panjin.anjuke.com'}, {'萍乡': 'https://pingxiang.anjuke.com'},
             {'濮阳': 'https://puyang.anjuke.com'}, {'莆田': 'https://putian.anjuke.com'},
             {'普洱': 'https://puer.anjuke.com'}, {'平凉': 'https://pingliang.anjuke.com'}, {'青岛': 'https://qd.anjuke.com'},
             {'秦皇岛': 'https://qinhuangdao.anjuke.com'}, {'泉州': 'https://quanzhou.anjuke.com'},
             {'曲靖': 'https://qujing.anjuke.com'}, {'齐齐哈尔': 'https://qiqihaer.anjuke.com'},
             {'衢州': 'https://quzhou.anjuke.com'}, {'清远': 'https://qingyuan.anjuke.com'},
             {'钦州': 'https://qinzhou.anjuke.com'}, {'庆阳': 'https://qingyang.anjuke.com'},
             {'黔东南': 'https://qiandongnan.anjuke.com'}, {'潜江': 'https://qianjiang.anjuke.com'},
             {'黔南': 'https://qiannan.anjuke.com'}, {'七台河': 'https://qitaihe.anjuke.com'},
             {'黔西南': 'https://qianxinan.anjuke.com'}, {'琼海': 'https://qionghai.anjuke.com'},
             {'日照': 'https://rizhao.anjuke.com'}, {'日喀则': 'https://rikeze.anjuke.com'},
             {'上海': 'https://shanghai.anjuke.com'}, {'深圳': 'https://shenzhen.anjuke.com'},
             {'苏州': 'https://suzhou.anjuke.com'}, {'石家庄': 'https://sjz.anjuke.com'}, {'沈阳': 'https://sy.anjuke.com'},
             {'三亚': 'https://sanya.anjuke.com'}, {'绍兴': 'https://shaoxing.anjuke.com'},
             {'汕头': 'https://shantou.anjuke.com'}, {'十堰': 'https://shiyan.anjuke.com'},
             {'三门峡': 'https://sanmenxia.anjuke.com'}, {'三明': 'https://sanming.anjuke.com'},
             {'韶关': 'https://shaoguan.anjuke.com'}, {'商丘': 'https://shangqiu.anjuke.com'},
             {'宿迁': 'https://suqian.anjuke.com'}, {'绥化': 'https://suihua.anjuke.com'},
             {'邵阳': 'https://shaoyang.anjuke.com'}, {'遂宁': 'https://suining.anjuke.com'},
             {'上饶': 'https://shangrao.anjuke.com'}, {'四平': 'https://siping.anjuke.com'},
             {'石河子': 'https://shihezi.anjuke.com'}, {'宿州': 'https://suzhoushi.anjuke.com'},
             {'松原': 'https://songyuan.anjuke.com'}, {'石嘴山': 'https://shizuishan.anjuke.com'},
             {'随州': 'https://suizhou.anjuke.com'}, {'朔州': 'https://shuozhou.anjuke.com'},
             {'汕尾': 'https://shanwei.anjuke.com'}, {'三沙': 'https://sansha.anjuke.com'},
             {'商洛': 'https://shangluo.anjuke.com'}, {'山南': 'https://shannan.anjuke.com'},
             {'神农架': 'https://shennongjia.anjuke.com'}, {'双鸭山': 'https://shuangyashan.anjuke.com'},
             {'天津': 'https://tianjin.anjuke.com'}, {'太原': 'https://ty.anjuke.com'},
             {'泰州': 'https://taizhou.anjuke.com'}, {'唐山': 'https://tangshan.anjuke.com'},
             {'泰安': 'https://taian.anjuke.com'}, {'台州': 'https://taiz.anjuke.com'},
             {'铁岭': 'https://tieling.anjuke.com'}, {'通辽': 'https://tongliao.anjuke.com'},
             {'铜陵': 'https://tongling.anjuke.com'}, {'天水': 'https://tianshui.anjuke.com'},
             {'通化': 'https://tonghua.anjuke.com'}, {'铜川': 'https://tongchuan.anjuke.com'},
             {'吐鲁番': 'https://tulufan.anjuke.com'}, {'天门': 'https://tianmen.anjuke.com'},
             {'图木舒克': 'https://tumushuke.anjuke.com'}, {'铜仁': 'https://tongren.anjuke.com'},
             {'武汉': 'https://wuhan.anjuke.com'}, {'无锡': 'https://wuxi.anjuke.com'}, {'威海': 'https://weihai.anjuke.com'},
             {'潍坊': 'https://weifang.anjuke.com'}, {'乌鲁木齐': 'https://wulumuqi.anjuke.com'},
             {'温州': 'https://wenzhou.anjuke.com'}, {'芜湖': 'https://wuhu.anjuke.com'},
             {'梧州': 'https://wuzhou.anjuke.com'}, {'渭南': 'https://weinan.anjuke.com'},
             {'乌海': 'https://wuhai.anjuke.com'}, {'武威': 'https://wuwei.anjuke.com'},
             {'乌兰察布': 'https://wulanchabu.anjuke.com'}, {'五家渠': 'https://wujiaqu.anjuke.com'},
             {'吴忠': 'https://wuzhong.anjuke.com'}, {'五指山': 'https://wuzhishan.anjuke.com'},
             {'文昌': 'https://wenchang.anjuke.com'}, {'五大连池': 'https://wudalianchi.anjuke.com'},
             {'万宁': 'https://wanning.anjuke.com'}, {'西安': 'https://xa.anjuke.com'}, {'厦门': 'https://xm.anjuke.com'},
             {'徐州': 'https://xuzhou.anjuke.com'}, {'湘潭': 'https://xiangtan.anjuke.com'},
             {'襄阳': 'https://xiangyang.anjuke.com'}, {'新乡': 'https://xinxiang.anjuke.com'},
             {'信阳': 'https://xinyang.anjuke.com'}, {'咸阳': 'https://xianyang.anjuke.com'},
             {'邢台': 'https://xingtai.anjuke.com'}, {'孝感': 'https://xiaogan.anjuke.com'},
             {'西宁': 'https://xining.anjuke.com'}, {'许昌': 'https://xuchang.anjuke.com'},
             {'忻州': 'https://xinzhou.anjuke.com'}, {'宣城': 'https://xuancheng.anjuke.com'},
             {'咸宁': 'https://xianning.anjuke.com'}, {'兴安盟': 'https://xinganmeng.anjuke.com'},
             {'新余': 'https://xinyu.anjuke.com'}, {'西双版纳': 'https://bannan.anjuke.com'},
             {'湘西': 'https://xiangxi.anjuke.com'}, {'仙桃': 'https://xiantao.anjuke.com'},
             {'锡林郭勒盟': 'https://xilinguole.anjuke.com'}, {'兴化': 'https://xinghua.anjuke.com'},
             {'烟台': 'https://yt.anjuke.com'}, {'扬州': 'https://yangzhou.anjuke.com'},
             {'宜昌': 'https://yichang.anjuke.com'}, {'银川': 'https://yinchuan.anjuke.com'},
             {'阳江': 'https://yangjiang.anjuke.com'}, {'永州': 'https://yongzhou.anjuke.com'},
             {'玉林': 'https://yulinshi.anjuke.com'}, {'盐城': 'https://yancheng.anjuke.com'},
             {'岳阳': 'https://yueyang.anjuke.com'}, {'运城': 'https://yuncheng.anjuke.com'},
             {'宜春': 'https://yichun.anjuke.com'}, {'营口': 'https://yingkou.anjuke.com'},
             {'榆林': 'https://yulin.anjuke.com'}, {'宜宾': 'https://yibin.anjuke.com'},
             {'益阳': 'https://yiyang.anjuke.com'}, {'玉溪': 'https://yuxi.anjuke.com'}, {'伊犁': 'https://yili.anjuke.com'},
             {'阳泉': 'https://yangquan.anjuke.com'}, {'延安': 'https://yanan.anjuke.com'},
             {'鹰潭': 'https://yingtan.anjuke.com'}, {'延边': 'https://yanbian.anjuke.com'},
             {'云浮': 'https://yufu.anjuke.com'}, {'雅安': 'https://yaan.anjuke.com'},
             {'伊春': 'https://yichunshi.anjuke.com'}, {'宜城': 'https://yicheng.anjuke.com'},
             {'郑州': 'https://zhengzhou.anjuke.com'}, {'珠海': 'https://zh.anjuke.com'}, {'中山': 'https://zs.anjuke.com'},
             {'镇江': 'https://zhenjiang.anjuke.com'}, {'淄博': 'https://zibo.anjuke.com'},
             {'张家口': 'https://zhangjiakou.anjuke.com'}, {'株洲': 'https://zhuzhou.anjuke.com'},
             {'漳州': 'https://zhangzhou.anjuke.com'}, {'湛江': 'https://zhanjiang.anjuke.com'},
             {'肇庆': 'https://zhaoqing.anjuke.com'}, {'枣庄': 'https://zaozhuang.anjuke.com'},
             {'舟山': 'https://zhoushan.anjuke.com'}, {'遵义': 'https://zunyi.anjuke.com'},
             {'驻马店': 'https://zhumadian.anjuke.com'}, {'自贡': 'https://zigong.anjuke.com'},
             {'资阳': 'https://ziyang.anjuke.com'}, {'周口': 'https://zhoukou.anjuke.com'},
             {'张家界': 'https://zhangjiajie.anjuke.com'}, {'张掖': 'https://zhangye.anjuke.com'},
             {'昭通': 'https://zhaotong.anjuke.com'}, {'中卫': 'https://weizhong.anjuke.com'},
             {'阿坝州': 'https://chengdu.anjuke.com'}, {'临安': 'https://hangzhou.anjuke.com'},
             {'万州': 'https://chongqing.anjuke.com'}, {'白沙县': 'https://haikou.anjuke.com'},
             {'儋州市': 'https://haikou.anjuke.com'}, {'澄迈县': 'https://haikou.anjuke.com'},
             {'定安': 'https://haikou.anjuke.com'}, {'琼中': 'https://haikou.anjuke.com'},
             {'屯昌': 'https://haikou.anjuke.com'}, {'文昌市': 'https://haikou.anjuke.com'},
             {'陵水': 'https://sanya.anjuke.com'}, {'琼海': 'https://sanya.anjuke.com'}, {'保亭': 'https://sanya.anjuke.com'},
             {'东方市': 'https://sanya.anjuke.com'}, {'兴化': 'https://taizhou.anjuke.com'},
             {'江都': 'https://yangzhou.anjuke.com'}, {'巴州': 'https://bazhong.anjuke.com'}]

import requests
import pika
import json
from lxml import etree
from lib.log import LogHandler
from retry import retry
import re

log = LogHandler('anjuke_producer_detail_url')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1',
    port=5673,
    heartbeat=0
))
channel = connection.channel()
channel.queue_declare(queue='anjuke_city_url_list',durable=True)
detail_channel = connection.channel()

class VerifyError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

class AnjukeProducer:
    def __init__(self,proxies):
        self.proxies = proxies
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(
        #     host='127.0.0.1',
        #     port=5673,
        #     heartbeat=0
        # ))
        # self.detail_channel = self.connection.channel()
        # self.channel = self.connection.channel()
        # # 以下队列中存放写字楼详情页的url
        # self.detail_channel.queue_declare(queue='loupan_office_detail_url', durable=True)
        # self.detail_channel.queue_declare(queue='new_office_detail_url', durable=True)
    def start_consume(self):
        # self.channel.basic_qos(prefetch_count=1)
        # self.channel.basic_consume(
        #     self.callback,
        #     queue='anjuke_city_url_list'
        # )
        # self.channel.start_consuming()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            self.callback,
            queue='anjuke_city_url_list'
        )
        channel.start_consuming()

    def callback(self,ch,method,properties,body):
        city_url = json.loads(body.decode())
        self.send_city_url(city_url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    @retry(logger=log,delay=2)
    def send_city_url(self,city_url):
        """
        :param city_url: https://shanghai.anjuke.com/
        :return:
        """
        res = requests.get(city_url,headers=self.headers,proxies=self.proxies)
        print(city_url)
        text = res.text
        if '访问验证-安居客' in text:
            raise VerifyError('出现滑块验证码')
        city_res = etree.HTML(res.content.decode())
        a_list = city_res.xpath('//div[@id="glbNavigation"]/div/ul/li/a')
        for a in a_list:
            name = a.xpath('text()')[0]
            if name == '商铺写字楼':
                main_url = a.xpath('@href')[0]
                log.info('该{}城市中包含商铺写字楼')
                self.send_list_url(main_url)
            if name == '新房':
                new_house_url = city_url + '/loupan/all/w5/'

        if '商铺写字楼' not in text and '新房' in text:
            log.info('该{}城市中不包含商铺写字楼，，但是含有新房'.format(city_url))

        else:
            city_res = etree.HTML(res.content.decode())
            a_list = city_res.xpath('//div[@id="glbNavigation"]/div/ul/li/a')
            # print(a_list)
            for a in a_list:
                name = a.xpath('text()')[0]
                if name == '商铺写字楼':
                    main_url = a.xpath('@href')[0]
                    log.info('该{}城市中包含商铺写字楼')
                    self.send_list_url(main_url)

    @retry(logger=log,delay=2)
    def send_list_url(self,main_url):
        """
        :param main_url:https://sh.xzl.anjuke.com/zu
        :return:解析出来写字楼列表页
        """
        try:
            res = requests.get(main_url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            log.error('该网站请求不到{}'.format(main_url))
            return
        list_res = etree.HTML(res.text)
        office_a_list = list_res.xpath('//div[@class="nav header-center clearfix"]/ul/li/a')
        if len(office_a_list) ==0:
            raise VerifyError('标签列表为空，出现滑块验证码')
        else:
            for a in office_a_list:
                office_name = a.xpath('text()')[0]
                if office_name == '写字楼新盘':
                    print(office_name)
                    #https://sh.fang.anjuke.com/xzl/all/p4_w5/
                    #base_new_url:https://sh.fang.anjuke.com/xzl/all/w5/
                    base_new_url = a.xpath('@href')[0]
                    print(base_new_url)
                    self.xzl_new_base(base_new_url)
                if office_name == '楼盘':
                    print(office_name)
                    #base_loupan_url:https://sh.xzl.anjuke.com/loupan/
                    #页数：https://sh.xzl.anjuke.com/loupan/p120/
                    base_loupan_url = a.xpath('@href')[0]
                    print(base_loupan_url)
                    result = re.search('(https.*com)', base_loupan_url)
                    if result:
                        base_url = result.group(1)
                        print(base_url)
                        for x in range(1, 200):
                            loupan_url = base_loupan_url + 'p' + str(x) + '/'
                            print(loupan_url)
                            result = self.parse_loupan(loupan_url,base_url)
                            if not result:
                                break

    @retry(logger=log,delay=2)
    def xzl_new_base(self,base_new_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_new = requests.get(base_new_url, headers=self.headers, proxies=self.proxies)
        if '访问验证-安居客' in res_new.text:
            raise VerifyError('出现滑块验证码')
        html_new = etree.HTML(res_new.text)
        total_num = html_new.xpath('//div[@class="key-sort"]/div[@class="sort-condi"]/span[@class="result"]/em/text()')
        if len(total_num)>0:
            total_num = total_num[0]
        else:
            total_num = 0
        total_page = int(int(total_num) / 50) + 1
        print(total_page)
        for x in range(1, total_page + 1):
            result = re.search('(.*?all/)', base_new_url).group(1)
            new_url = result + 'p' + str(x) + '_w5/'
            print(new_url)
            res_new_page = self.xzl_new_page(new_url)
            self.parse_new(res_new_page)

    @retry(logger=log,delay=2)
    def xzl_new_page(self,new_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_new_page = requests.get(new_url, headers=self.headers, proxies=self.proxies)
        if '访问验证-安居客' in res_new_page.text:
            raise VerifyError('出现滑块验证码')
        else:
            return res_new_page

    def parse_new(self,res_new_page):
        html_new = etree.HTML(res_new_page.text)
        detail_urls = html_new.xpath('//div[@class="list-results"]/div[@class="key-list"]/div/@data-link')
        detail_channel.basic_publish(
            exchange='',
            routing_key='new_office_detail_url',
            body=json.dumps(detail_urls),
            properties=pika.BasicProperties(delivery_mode=2,)
            )
        print('将新盘的一页放入到队列中{}'.format(res_new_page.url))


    @retry(logger=log, delay=2)
    def parse_loupan(self, loupan_url,base_url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res_loupan = requests.get(loupan_url, headers=self.headers, proxies=self.proxies)
        if '访问验证-安居客' in res_loupan.text:
            raise VerifyError('出现滑块验证码')
        html_loupan = etree.HTML(res_loupan.text)
        none_tag = html_loupan.xpath('//div[@class="layout"]/div[@id="list-content"]/div[@class="comhead"]/div[@class="noresult-tips"]/text()')
        print(none_tag)
        if len(none_tag) > 0:
            log.error('{}没有更多搜索结果了'.format(res_loupan.url))
            return False
        else:
            # 获取每一个写字楼详情页的url,并将每一页所有的写字楼链接放入到一个列表中。并将其放入到队列中
            #detail_url :/loupan/382271
            detail_urls = html_loupan.xpath('//div[@class="layout"]/div[@id="list-content"]/div[@class="list-item"]/@link')
            if len(detail_urls) == 0:
                return False
            detail_dict = {}
            detail_dict[base_url] = detail_urls
            print(detail_dict)
            detail_channel.basic_publish(
                exchange='',
                routing_key='loupan_office_detail_url',
                body=json.dumps(detail_dict),
                properties=pika.BasicProperties(delivery_mode=2, )
            )
            print('将楼盘的一页放入到队列中{}'.format(loupan_url))
            return True


if __name__ == '__main__':
    AnjukeProducer(proxies=next(p)).start_consume()













