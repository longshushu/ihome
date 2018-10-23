# coding=utf-8

from flask import g, request, jsonify, current_app
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required
from ihome import db, redis_store
from ihome.api_1_0 import api
from datetime import datetime
from ihome.models import Houses, Order


@api.route("/orders", methods=["POST"])
@login_required
def save_order_info():
    # 保存订单信息
    # 获取用户的id
    user_id = g.user_id
    # 从前端获取参数
    orders_dict = request.get_json()
    # 判断参数是否完整
    if not orders_dict:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取参数并校验完整性
    start_date_str = orders_dict.get("start_date")
    end_date_str = orders_dict.get("end_date")
    house_id = orders_dict.get("house_id")
    if not all([start_date, end_date, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验时间格式
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date
        # 计算预订的天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.PARAMERR, errmsg="时间格式错误")
    # 查询房屋是否存在
    try:
        house = Houses.query.get(house_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg="数据异常")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="获取房屋信息失败")
    # 判断预订房屋的是否是房东自己
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预订自己的房屋")
    # 检查在预订的时候该房屋是否已经被预订了
    try:
        # 查询时间冲突的订单数
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date, Order.end_date >= start_date).count()
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg="检查出错，请稍后再试")
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已经被预订")
    # 计算房屋的总价
    amount = days * house.price
    # 保存订单的信息
    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.errno(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单出错")
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


# 查询用户的订单信息，这其中包括两种情况，一种是房东查询自己的被预订的，一种是用户查询自己预订的
# 将两种合并在一个视图中，在传送过来的URL中通过参数进行区分
# api/v1.0/user/orders?role = xxxxx
@api.route("user/orders", methods=["GET"])
@login_required
def get_user_orders():
    # 查询用户的订单信息
    user_id = g.user_id
    # 用户的身份，用户想要查询作为房客预订别人房子的订单，还是想要作为房东查询别人预订自己房子的订单
    role = request.args.get("role", "")
    # 房东查询自己被预订的房屋
    try:
        if role == "landlord":
            # 以房东的身份查询订单
            # 先查询属于自己的房子有哪些
            houses = Houses.query.filter(Houses.user_id == user_id).all()
            house_ids = (house.id for house in houses)
            # 再查询预订了自己房子的订单
            orders = Order.query.filter(Order.house_id.in_(house_ids)).order_by(Order.create_time.desc()).all()
        else:
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据库失败")
    # 将得到的数据转换为字典
    orders_dict_list = []
    for order in orders:
        orders_dict_list.append(order.to_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": orders_dict_list})


# 商家接单和拒绝接单
@api.route("/orders/<int:order_id>/status/", methods=["PUT"])
@login_required
def accept_reject_order(order_id):
    # 接单与拒绝接单
    user_id = g.user_id
    # 前端需要传送过来的参数
    data_dict = request.get_json()
    # 判断参数是否存在
    if not data_dict:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 房东的操作行为, action参数表明客户端请求的是接单还是拒单的行为
    action = data_dict.get("action")
    if action not in("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 根据订单号查询订单，并且要求订单处于等待接单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").all()
        house = order.house
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg="无法获取订单信息")
    # 确保房东只能修改属于自己房子的订单
    if not order or house.user_id != user_id:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")
    # 判断房东的操作
    if action == "accept":
        # 接单，将订单状态设置为等待评论
        order.status = "WAIT_PAYMENT"
    elif action == "reject":
        # 拒单，要求用户传递拒单原因
        reason = data_dict.get("reason")
        if not reason:
            return jsonify(errno=RET.DATAERR, errmsg="拒单必须要写拒绝理由")
        order.comment = reason
        order.status = "REJECTED"
    # 将数据库的内容进行更新
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.errno(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存异常")
    return jsonify(errno=RET.OK, errmsg="OK")


# 评价信息的
@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_required
def save_order_comment(order_id):
    # 评论信息的保存
    user_id = g.user_id
    # 获取参数
    data_dict = request.get_json()
    comment = data_dict.get("comment")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="没有数据")
    # 用户只能对自己的订单进行操作
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_COMMENT", Order.user_id == user_id).first()
        house = order.house
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.NODATA, errmsg="查询订单是出现错误")
    if not order:
        return jsonify(errno=RET.REQERR, errmsg="无效的操作")
    try:
        # 将订单的状态设置为完成
        order.status = "COMPLETE"
        order.comment = comment
        # 将房屋的订单数加上1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.errno(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存信息时出现错误")
    #  # 因为房屋详情中有订单的评价信息，为了让最新的评价信息展示在房屋详情中，所以删除redis中关于本订单房屋的详情缓存
    try:
        redis_store.delete("house_info_%s" % order.house_id)
    except Exception as e:
        current_app.logger.errno(e)
    return jsonify(errno=RET.OK, errmsg="OK")



