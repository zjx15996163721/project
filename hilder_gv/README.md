**How to run?**
--
cd /hilder_gv/python run.py

<a href='http://192.168.0.27/DataProduct/hilder_gv/wikis/%E9%A1%B9%E7%9B%AE%E5%86%85%E6%8A%80%E6%9C%AF%E7%BB%86%E8%8A%82'>开发细节</a>

**Hilder Government Crawler**
--
政府多个网站抓取，批量管理

**How to start this?**
--
git pull git@192.168.0.27:DataProduct/hilder_gv.git

**What lib?**
--
see lib <a href='http://192.168.0.27/DataProduct/lib/wikis/How-to-start-submodule%3F'>LIB WIKI</a> 

字段
--
`小区`

co_index  # 网站id

co_name  # 小区名称

co_id  # 小区id

co_address  # 小区地址

co_type  # 小区类型/物业类型 :商品房/商品房/别墅

co_build_type  # 建筑类型:独栋,小高层,高层多层

co_green  # 绿化率

co_is_build  # 竣工/是否在建 1 已经完成/竣工 0未完成/正在建立

co_size  # 占地面的

co_build_size  # 建筑面积

co_build_start_time  # 开工时间

co_build_end_time  # 竣工时间

co_investor  # 投资商

co_develops  # 开发商

co_pre_sale  # 预售证书

co_pre_sale_date  # 预售证书日期

co_open_time  # 小区开盘时间

co_handed_time  # 小区交房时间

co_all_house  # 小区总套数

co_land_use  # 土地使用证

co_volumetric  # 容积率

co_owner  # 房产证/房屋所有权证

co_build_structural  # 建筑结构：钢筋混泥土

`楼栋`

co_index  # 网站id

co_id  # 小区id

bu_id  # 楼栋id

bu_name  # 楼栋名称

bu_num  # 楼号 栋号

bu_all_house  # 总套数

bu_floor  # 楼层

bu_build_size  # 建筑面积

bu_live_size  # 住宅面积

bu_not_live_size  # 非住宅面积

bu_price  # 住宅价格

bu_pre_sale  # 楼栋预售证书

bu_pre_sale_date  # 楼栋预售证书日期

`房号`

co_index  # 网站id

co_id  # 小区id

bu_id  # 楼栋id

ho_name  # 房号：3单元403

ho_num  # 房号id

ho_floor  # 楼层

ho_type  # 房屋类型：普通住宅 / 车库仓库

ho_room_type  # 户型：一室一厅

ho_build_size  # 建筑面积

ho_true_size  # 预测套内面积,实际面积

ho_share_size  # 分摊面积

ho_price  # 价格

orientation  # 朝向


