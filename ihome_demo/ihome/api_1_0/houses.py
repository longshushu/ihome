# coding=utf-8

from ihome.api_1_0 import api
from ihome import redis_store, constants, db
from ihome.models import Area, Houses, Facility, User, Order
from flask import current_app, jsonify, request, g
import json
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from datetime import datetime


# 获取城区的信息
@api.route("/area")
def get_area_info():
    # 获取城区的信息
    # 获取城区的思路：为了使得能够不进行太频繁的数据库的交流，因此可以将城区的信息存储到REDIS中
    # 在读取城区的信息时先从redis缓存中读取，读取不到时再在数据库中进行读取
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            return resp_json, 200, {"Content-Type": "application/json"}
    # 当redis中没有相应的缓存的时候，就从数据库中读取数据
    try:
        # 读取数据库得到关于地区的对象
        areas = Area.query.all()
        # 通过遍历得到对应的具体的内容
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取异常")
    area_info_li = []
    for area in areas:
        area_info_li.append(area.area_to_dict())
    # 将数据转化为json格式的数据
    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_info_li)
    resp_json = json.dumps(resp_dict)
    # 将数据存储到redis中
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)
    return resp_json, 200, {"Content-Type": "application/json"}


# 用户填写的房屋基本信息的获取
@api.route("/user/info", methods=["POST"])
@login_required
def get_house_info():
    # 前端发送过来的json数据
    """
    {
        "title": "",
        "price": "",
        "area_id": "1",
        "address": "",
        "room_count": "",
        "size": "",
        "unit": "",
        "capacity": "",
        "beds": "",
        "deposit": "",
        "min_days": "",
        "max_days": "",
        "facility": ["7", "8"]
    }
    """
    user_id = g.user_id
    # 获取参数
    data_dict = request.get_json()
    title = data_dict.get("title")
    price = data_dict.get("price")
    area_id = data_dict.get("area_id")
    address = data_dict.get("address")  # 房屋地址
    room_count = data_dict.get("room_count")  # 房屋包含的房间数目
    size = data_dict.get("acreage")  # 房屋面积
    unit = data_dict.get("unit")  # 房屋布局（几室几厅)
    capacity = data_dict.get("capacity")  # 房屋容纳人数
    beds = data_dict.get("beds")  # 房屋卧床数目
    deposit = data_dict.get("deposit")  # 押金
    min_days = data_dict.get("min_days")  # 最小入住天数
    max_days = data_dict.get("max_days")  # 最大入住天数
    # 校验参数的完整性
    if not all([title, price, area_id, address, room_count, size, unit, capacity, beds, deposit, max_days, min_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验价格和押金是否是合法的数据
    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 校验地区是否是合法的
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="城区信息有误")
    # 保存房屋信息
    house = Houses(title=title,
                   user_id= user_id,
                   price=price,
                   area_id=area_id,
                   address=address,
                   room_count=room_count,
                   size=size,
                   unit=unit,
                   capacity=capacity,
                   beds=beds,
                   deposit=deposit,
                   min_days=min_days,
                   max_days=max_days
                   )
    # 处理房屋设施的信息
    facility_ids = data_dict.get("facility")
    try:
        # select  * from ih_facility_info where id in []
        facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if facilities:
        # 表示有合法的设施数据
        # 保存设施数据
        house.facilities = facilities
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存房屋异常")
    return jsonify(errno=RET.OK, errmsg="ok", data={"house_id":  house.id})


# 保存房屋的图片信息
@api.route("/user/image", methods=["POST"])
@login_required
def save_house_image():
    # 接受的参数为房屋的id 和房屋的图片
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验房屋的编号是否合法
    try:
        house = Houses.query.get(id=house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")
    image_data = image_file.read()
    # 将图片保存到第三方的服务器中
    # 将数据保存到数据库中


@api.route("/user/houses/", methods=["GET"])
@login_required
def get_user_house():
    # 用户发表的房屋的房源
    # 获取用户的ID
    user_id = g.user_id
    # print(user_id)
    # 获取用户所对应的发布的房屋的数量
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    # 将查询到的房屋信息放到列表中返回
    houses_li = []
    if houses:
        for house in houses:
            houses_li.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="ok", data={"houses": houses_li})


@api.route("/user/index", methods=["GET"])
def get_house_index():
    # 获取房屋的主页的信息
    # 尝试从redis中获取数据
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        # 由于redis中存储的数据就是字符串类型的数据，因此可以直接将其返回而不用在利用jsonify进行转换
        return '{"errno": 0, "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        # 进行数据库的查询
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            houses = Houses.query.filter_by(Houses.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="查询数据库异常")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")
        houses_list = []
        for house in houses:
            # 如果用户没有设置主页的图片，则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())
        # 将json数据转换成字符串类型的数据存放redis中
        json_house = json.dumps(houses_list)
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_house)
        except Exception as e:
            current_app.logger.error(e)
        return '{"errno": 0, "errmsg":"OK", "data": %s}' % json_house, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    # 获取房屋的详细的信息
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1

    user_id = session.get("user_id", "-1")
    # 校验参数是否完整
    if not house_id:
        return jsonify(errno=RET.DATAERR, errmsg="参数不完整")
    # 由于房屋的详细信息也是大量访问的信息，因此需要将其存放到redis中，所以先尝试从缓存中读取数据
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        return '{"errno": 0, "errmsg":"OK", "data": {"user_id": %s, "house": %s}}' % (user_id, ret), 200, \
                {"Content-Type": "application/json"}
    # 查询数据库
    try:
        house = Houses.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")
    # 将房屋的信息转化为字典测形式
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")
    # 将房屋的信息存放到redis中去
    house_json = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, house_json)
    except Exception as e:
        current_app.logger.error(e)
    resp =  '{"errno": 0, "errmsg":"OK", "data": {"user_id": %s, "house": %s}}' % (user_id, ret), 200, \
           {"Content-Type": "application/json"}
    return resp


# GET /api/v1.0/houses?sd=2017-12-01&ed=2017-12-31&aid=10&sk=new&p=1
@api.route("/houses")
def get_house_list():
    """获取房屋的列表列表信息（搜索页面）"""
    start_date = request.args.get("sd", "")  # 用户想要的开始的时间
    end_date = request.args.get("ed", "")  # 用户想要的结束的时间
    area_id = request.args.get("aid", "")  # 用户输入的城区的id
    sort_key = request.args.get("sk", "new")  # 用户输入的排序的关键字
    page = request.args.get("p")  # 页数
    # 校验用户传来的时间
    try:
        # 因为传过来的是字符串的格式，所以需要用datetime将它转化为时间的格式
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="时间参数错误")
    # 处理传过来的区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")
    # 处理传来的参数中的页数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 获取缓存数据
    # 由于该列表页面也是大量的访问，所以也要将其存放在redis中
    # 因为为了满足在同一个区域的一页内容更新后其余的所有的页面的内容都得更新，因此需要将其用hash的方式进行存储
    # "house_起始_结束_区域id_排序": hash
    # {
    #     "1": "{}",
    #     "2": "{}",
    # }
    redis_key = "house_%s-%s-%s-%s" %(start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}
    # 如果缓存中没有数据，那么需要从数据库中进行读取
    # 首先在读取的时候要将预订了的订单排除
    # 过滤条件的参数的列表容器
    filter_params =[]
    # 进行过滤 首先是时间范围内的订单
    conflict_orders = None
    try:
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= end_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # 如果订单数存在，找出订单存在的房屋的额id
    if conflict_orders:
        conflict_house_ids = (order.house_id for order in conflict_orders)
        # 如果冲突的房屋的id中不是空的，向查询参数中添加条件,即将冲突的房屋的房屋的id排除在外
        if conflict_house_ids:
            filter_params.append(Houses.id.notin_(conflict_house_ids))
    # 区域条件
    if area_id:
        filter_params.append(Houses.area_id == area_id)
    # 处理查询关键字的条件
    if sort_key == "booking":  # 订单入住量
        house_query = Houses.query.filter(*filter_params).order_by(Houses.order_count.desc())
    elif sort_key == "price-inc":
        house_query = Houses.query.filter(*filter_params).order_by(Houses.price.asc())
    elif sort_key == "price-des":
        house_query = Houses.query.filter(*filter_params).order_by(Houses.price)
    else:  # 默认或者当用户点击新旧是按照这个排序
        house_query = Houses.query.filter(*filter_params).order_by(Houses.create_time.desc())
    try:
        # 处理分页的信息
        #                               当前的页数     每一页的条数                                  自动的错误输出
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # 获取每一页的内容
    houses = []
    house_li = page_obj.items
    for house in house_li:
        houses.append(house.to_basic_dict())
    # 获取总的页数
    total_page = page_obj.pages
    resp_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
    resp_json = json.dumps(resp_dict)
    # 将数据存储到redis中,存储的格式为hash
    if page <= total_page:
        redis_key = "house_%s-%s-%s-%s" %(start_date, end_date, area_id, sort_key)
        try:
            # redis_store.hset(redis_key, page, resp_json)
            # redis.expires(redis_key, constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
            # 能够进行多条信息的提交
            pipeline = redis_store.pipeline()
            pipeline.multi()  # 开启多个语句的记录
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expires(redis_key, constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
            pipeline.execute()  # 执行语句进行管道村春语句
        except Exception as e:
            current_app.logger.error(e)
            # return jsonify(errno=RET.DBERR, errmsg="保存数据异常")
    return resp_json, 200, {"Content-Type": "application/json"}


